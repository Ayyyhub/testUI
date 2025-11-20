"""
图片对比模块 - 使用大模型进行图片内容对比分析
支持同步和异步调用
"""
import os
import base64
import glob
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from dashscope import MultiModalConversation


class ImageComparison:
    def __init__(self, compare_base_dir="compare_base"):
        self.compare_base_dir = compare_base_dir
        self.executor = ThreadPoolExecutor(max_workers=3)  # 异步执行器


    """将本地图片转换为Base64编码"""
    def local_image_to_base64(self, image_path):

        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    """根据截图文件名匹配对应的基准图片"""
    def find_matching_base_image(self, screenshot_path):

        # 提取截图的基本名称（去除时间戳）
        screenshot_name = os.path.basename(screenshot_path)
        parts = screenshot_name.split("_")
        if len(parts) >= 3:
            # 提取前三个部分：screenshot、workflow、数字
            base_name = f"{parts[0]}_{parts[1]}_{parts[2]}_{parts[3]}"  # 获取类似 "screenshot_workflow_01" 的字符串
        else:
            print(f"⚠️ 截图文件名格式不正确：{screenshot_name}")
            return None

        print(f"🔍 查找匹配的基准图片，base_name: {base_name}")

        # 在compare_base目录中查找
        pattern = os.path.join(self.compare_base_dir, f"{base_name}*.png")
        matching_files = glob.glob(pattern)

        if matching_files:
            print(f"✅ 在基准目录中找到匹配的图片：{matching_files[0]}")
            return matching_files[0]  # 返回第一个匹配到的带目录的文件

        print(f"⚠️ 在 {self.compare_base_dir} 下未找到匹配的基准图片: {base_name}")
        return None


    """直接调用ai对比分析两张图片"""
    def direct_comparison_analysis(self, image1_path, image2_path) ->str:

        # 转换为Base64
        image1_base64 = self.local_image_to_base64(image1_path)
        image2_base64 = self.local_image_to_base64(image2_path)

        # 截图图片
        image1_data_uri = f"data:image/png;base64,{image1_base64}"
        # 基准图片
        image2_data_uri = f"data:image/png;base64,{image2_base64}"
        
        prompt_text = """请直接对比分析这两张图片是否一致，重点关注以下三个核心方面：
        
            1. 左侧结构树：左侧场景层次下的内容和布局是否相同（无需考虑标签页不同情况）;
            2. 机器人姿态：页面中机器人（如有）的运动姿态和运动位置是否一致;
            3. 异常内容：检查页面中是否有不该出现的元素或弹窗（左下角系统提示框信息若有价值可作为参考）;
            4. 布局一致性：整体页面布局是否与基准图片一致;
            
            请直接回答：是否一致？如果一致请说"一致"，如果不一致请说明具体差异。"""
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image1_data_uri},
                    {"type": "image", "image": image2_data_uri},
                    {"type": "text", "text": prompt_text}
                ]
            }
        ]
        
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            return "错误：未配置DASHSCOPE_API_KEY环境变量"
        
        try:
            response = MultiModalConversation.call(
                model="qwen3-vl-plus",
                messages=messages,
                api_key=api_key
            )
            
            if hasattr(response, 'output') and response.output.choices:
                return response.output.choices[0].message.content
            else:
                return f"调用失败：{getattr(response, 'code', '未知错误')}"
        except Exception as e:
            return f"调用过程抛出异常：{str(e)}"

    """使用上下文信息进行增强的AI对比分析"""
    def enhanced_comparison_analysis(self, image1_path, context_info) ->str:

        # 转换为Base64
        image1_base64 = self.local_image_to_base64(image1_path)

        image1_data_uri = f"data:image/png;base64,{image1_base64}"

        # 构建包含上下文信息的提示词
        prompt_text = f"""请基于当前截图和以下测试步骤上下文信息，分析登记失败或者断言失败的原因，给出结论即可：

        {context_info}
        
        对比分析要求：
        1. context_info包含当前执行步骤，以及上下文信息；
        2. 根据当前截图分析断言失败或者selenium操作元素的失败原因；
        背景：
        0. 每次执行一个工作流都是从一个新建的场景中从0开始操作的；
        1. 目前此ui自动化是以DDT测试数据驱动来进行的，元素的路径都存在excell里面；
        2. 主要情况有当前步骤点击成功，但断言异常进行截图，和当前步骤点击失败，但断言异常进行截图两种情况；
        3. excell里面的结构为：业务流程ID   流程描述 	步骤序号	操作类型	 定位方式（click等类型）  定位值（当前操作的唯一路径）	input输入数据  可视化检测点（主动截屏的点）  预期结果（预期结果的路径）  实际结果	测试状态；
        4. excell里面的预期结果可能并不针对当前的执行步骤，也有可能是断言下一步操作的元素是否可见或者存在；
        5. 在分析时一般会出现以下常见问题：一、定位值路径不正确导致操作当前步骤失败或者预期结果的路径不正确断言预期结果步骤失败；二、定位元素的路径存在但是当前操作步骤被遮挡，导致无法执行当前步骤；
        
        请基于上下文信息给出详细分析，并给出分析后可能的原因。
        例如，原因一：
             原因二：
             ......
        """
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image1_data_uri},

                    {"type": "text", "text": prompt_text}
                ]
            }
        ]
        
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            return "错误：未配置DASHSCOPE_API_KEY环境变量"
        
        try:
            response = MultiModalConversation.call(
                model="qwen3-vl-plus",
                messages=messages,
                api_key=api_key
            )
            
            if hasattr(response, 'output') and response.output.choices:
                return response.output.choices[0].message.content
            else:
                return f"调用失败：{getattr(response, 'code', '未知错误')}"
        except Exception as e:
            return f"调用过程抛出异常：{str(e)}"
    

    """异步对比截图和基准图片 - 不阻塞主线程"""
    def async_compare_images(self, screenshot_path,  context_info=""):

        def _async_task():
            try:
                # 传递完整的截图目录
                screenshot_exam = os.path.join("screenshoot_dir", screenshot_path)

                print(f"🚀 准备进行异步AI对比分析：")

                # 如果有上下文信息，使用增强的对比分析
                if context_info :
                    print(f"   包含上下文信息：{len(context_info)}字符")
                    comparison_result = self.enhanced_comparison_analysis(screenshot_exam, context_info)

                    print(f"✅ AssertFailed异步AI对比完成：{comparison_result}")
                    self._save_async_result(screenshot_path=screenshot_exam, result=comparison_result)

                else:

                    # 查找匹配的基准图片
                    base_image_path = self.find_matching_base_image(screenshot_exam)

                    if not base_image_path:
                        print(f"⚠️ 异步对比：未找到匹配的基准图片：{screenshot_exam}")
                        return
                    # 如果没有上下文信息，直接对比
                    comparison_result = self.direct_comparison_analysis(screenshot_exam, base_image_path)
                
                    print(f"✅ Proactive异步AI对比完成：{comparison_result}")
                    # 这里可以添加结果处理逻辑，比如写入日志或数据库
                    self._save_async_result(base_image_path=base_image_path,screenshot_path=screenshot_exam, result=comparison_result)
                
            except Exception as e:
                print(f"❌ 异步AI对比失败：{str(e)}")
        
        # 在线程池中异步执行
        future = self.executor.submit(_async_task)
        return future

    """保存异步对比结果"""
    def _save_async_result(self, screenshot_path, result, base_image_path=""):

        try:
            # 创建结果目录
            result_dir = "ai_comparison_results"
            os.makedirs(result_dir, exist_ok=True)
            
            # 生成结果文件名
            filename = os.path.basename(screenshot_path).replace('.png', '_ai_result.txt')
            result_file = os.path.join(result_dir, filename)
            
            # 写入结果
            with open(result_file, 'w', encoding='utf-8') as f:
                # 判断是断言调用还是主动调用
                if base_image_path:
                    # 主动调用逻辑：有基准图片
                    f.write(f"对比类型: 主动截图对比\n")
                    f.write(f"基准图片：{base_image_path}\n")
                else:
                    # 断言调用逻辑：无基准图片
                    f.write(f"对比类型: 断言失败分析\n")
                    f.write(f"基准图片：无（断言失败分析）\n")
                
                f.write(f"截图文件: {screenshot_path}\n")
                f.write(f"对比时间: {os.path.basename(screenshot_path).split('_')[-1].replace('.png', '')}\n")
                f.write(f"AI对比结果: {result}\n")
                f.write("=" * 50 + "\n")
            
            print(f"📄 异步对比结果已保存：{result_file}")
            
        except Exception as e:
            print(f"⚠️ 保存异步结果失败：{str(e)}")







# def demo_image_comparison():
#     """演示图片对比功能"""
#     comparator = ImageComparison()
#
#     # 测试一个截图文件
#     test_screenshot = "screenshot_workflow_24_20251110_201625.png"
#
#     if os.path.exists(test_screenshot):
#         result = comparator.compare_images(test_screenshot)
#         print("\n✅ 对比完成")
#     else:
#         print("测试截图文件不存在，请先运行测试生成截图")
#
# """对比截图和基准图片"""
# def compare_images(self, screenshot_path, comparison_type="structure"):
#
#     # 查找匹配的基准图片
#     base_image_path = self.find_matching_base_image(screenshot_path)
#
#     if not base_image_path:
#         return f"未找到匹配的基准图片：{screenshot_path}"
#
#     print(f"🔍 开始对比分析：")
#     print(f"   截图文件：{screenshot_path}")
#     print(f"   基准图片：{base_image_path}")
#
#     # 使用直接对比方法
#     print("\n📊 直接对比分析结果：")
#     comparison_result = self.direct_comparison_analysis(screenshot_path, base_image_path, comparison_type)
#     print(comparison_result)
#
#     return {
#         "comparison_result": comparison_result,
#         "base_image_path": base_image_path
#     }
#
# if __name__ == '__main__':
#     demo_image_comparison()