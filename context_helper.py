from image_comparison import ImageComparison

class Context_Helper:
    """统一的AI图片对比分析入口方法"""

    @staticmethod
    def async_ai_comparison(screenshot_path, current_data=None, test_data_list=None):
        """
        统一的AI图片对比分析入口方法
        Args:
            screenshot_path: 截屏图片路径
            current_data: 当前测试数据（用于断言失败场景，可选）
            test_data_list: 测试数据上下文列表（用于断言失败场景，可选）:"[()]"
        """
        try:
            comparator = ImageComparison()
            context_info = ""

            # ==== 判断是否需要上下文，如有上下文 ====
            if current_data and test_data_list:
                context_data = Context_Helper.get_context_data(current_data, test_data_list, 2)
                context_info = Context_Helper.format_context_for_ai(context_data, current_data.step_id)
                print(f"📋 已添加上下文信息到AI分析（{len(context_data)}个步骤）")
                print("   该调用来自断言失败场景（带上下文）")

            else:
                print("🟢 正向主动截屏（无上下文信息）")

            # ==== 异步调用AI对比 ====
            comparator.async_compare_images(screenshot_path, context_info=context_info)
            print(f"🚀 AI分析任务已提交（异步执行）: {screenshot_path}")
            print("   主流程继续执行，不受AI分析影响")

        except Exception as e:
            print(f"⚠️ 异步AI对比提交失败: {str(e)}")


    """获取当前测试步骤的上下文数据"""
    @staticmethod
    def get_context_data(current_data, test_data_list, context_range):

        try:
            current_index = next(
                (i for i, d in enumerate(test_data_list)
                 if d.step_id == current_data.step_id and d.test_case_id == current_data.test_case_id),
                -1
            )

            if current_index == -1:
                print(f"⚠️ 未找到当前步骤索引: {current_data.step_id}")
                return []

            start_index = max(0, current_index - context_range)
            end_index = min(len(test_data_list), current_index + context_range + 1)
            context_data = test_data_list[start_index:end_index]

            print(f"📋 获取到上下文数据: 步骤 {current_data.step_id} 附近共 {len(context_data)} 个步骤")
            for i, data in enumerate(context_data):
                prefix = "→" if data.step_id == current_data.step_id else "  "
                print(f"{prefix} 步骤 {data.step_id}: {data.description}")

            return context_data
        except Exception as e:
            print(f"⚠️ 获取上下文数据失败: {str(e)}")
            return []

    """格式化上下文数据为AI可理解的文本"""
    @staticmethod
    def format_context_for_ai(context_data, current_step_id):
        try:
            context_text = "测试步骤上下文信息:\n"
            for data in context_data:
                marker = " [当前步骤]" if data.step_id == current_step_id else ""
                context_text += f"步骤 {data.step_id}{marker}: {data.description}\n"

                if data.determin_type:
                    context_text += f"   操作类型: {data.determin_type}"
                    if data.determin_method and data.determin_value:
                        context_text += f", 定位方式: {data.determin_method}, 定位值: {data.determin_value}"
                    if data.input_value:
                        context_text += f", 输入值: {data.input_value}"
                    context_text += "\n"

                if data.expected_result:
                    context_text += f"   预期结果: {data.expected_result}\n"

                context_text += "\n"

            return context_text
        except Exception as e:
            print(f"⚠️ 格式化上下文数据失败: {str(e)}")
            return "上下文信息获取失败"
