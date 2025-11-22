import os
import base64
from testcases.newcreate_helper import NewcreateHelper
import glob
from conftest import driver
from qwen_compare.context_helper import Context_Helper

from core.execute_test_data import UITestExecutor
from Log.logger import logger
from qwen_compare.opencv import opencv_screenshot
from testcases.login_helper import LoginHelper
from utils.conf_reader import load_config
from utils.excell_reader import Excellreader
import time
from core.assertion import customed_assertion


class Test_truework03:
    def __init__(self):
        self.driver = None  # 构造函数中初始化driver属性
        self.test_results = []  # 在 __init__ 中初始化
        self.current_sheet = ""  # 在 __init__ 中初始化

    def test_truework03_func(self, driver):
        self.driver = driver  # 将传入的方法参数 driver 保存为实例变量，以便 self.driver 在类的其他方法中使用
        self.test_results = []
        self.current_sheet = "PathGenerator" # 路径生成程序工程流
        # 1. 执行登录测试
        test_login_example = LoginHelper()
        test_login_example.login_func(self.driver)
        # 2. 点击新建
        new_create = NewcreateHelper()
        new_create.newcreate_func(self.driver)
        print("=== 开始执行work_flow03 ===" + "\n")

        # actions = ActionChains(self.driver)
        config = load_config()
        excell_path = config["excell_path"]
        excell_reader = Excellreader(excell_path)
        test_data_list3 = excell_reader.get_test_data(sheet_name=self.current_sheet)
        cs_assert = customed_assertion(self.driver)

        for data in test_data_list3:
            # get_context_data 获取上下文数据
            context_data_list = Context_Helper.get_context_data(data, test_data_list3, 2)

            if data:
                print("=" * 50)
                logger.info(f"执行测试用例：{data}")

                # monitor.start() 性能监控
                try:
                    # 执行excell元素流程测试
                    execute = UITestExecutor(self.driver)
                    execute.execute_step(data)

                    # 判断断言方式
                    if data.assert_type == "visible":
                        # 断言成功
                        if cs_assert.assert_element_visible(data.assert_method, data.expected_result):
                            # 检查cv_points字段，如果为 TRUE 则 主动截屏！
                            if data.cv_points and str(data.cv_points).upper() == "TRUE":
                                try:
                                    # 生成截屏文件名
                                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                                    active_screenshot_path = f"Proactive_{self.current_sheet}_{data.test_case_id}_{timestamp}.png"

                                    # 等待机器人运动完成（关键修复：确保在正确时机截屏）
                                    print("⏳ 等待系统加载完成...")
                                    time.sleep(3)  # 等待3秒让机器人完成运动

                                    # 1、====== 主动截屏，不需要上下文 ======
                                    opencv_screenshot(active_screenshot_path, self.driver)
                                    # 异步调用AI对比图片
                                    Context_Helper.async_ai_comparison(active_screenshot_path)

                                except Exception as screenshot_error:
                                    print(f"❌ 主动截屏失败：{str(screenshot_error)}")

                            logger.info(f"断言成功，测试结果汇总：步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                            # print(f"步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                            print("=" * 50 + "\n")

                        # 断言失败
                        else:
                            try:
                                data.status = "FAIL"
                                data.outputed_result = f"断言失败：预期元素 {data.expected_result} 不可见"
                                print(f"断言失败准备截屏...")

                                # 2、====== 异步调用AI图片对比分析（断言失败需要需要上下文）======
                                # 断言失败截屏文件名
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                assertfail_screenshot_name = f"AssertFailed_{self.current_sheet}_{data.test_case_id}_{timestamp}.png"

                                # 调用截屏方法
                                opencv_screenshot(assertfail_screenshot_name, self.driver)

                                # 调用异步ai分析图片断言失败原因（断言失败需要需要上下文）
                                Context_Helper.async_ai_comparison(screenshot_path=assertfail_screenshot_name,
                                                                   current_data=data,
                                                                   test_data_list=context_data_list)
                            except Exception as screenshot_error:
                                print(f"❌ 断言截屏失败：{str(screenshot_error)}")

                    elif data.assert_type == "closed":
                        if cs_assert.assert_popup_closed(data.assert_method, data.expected_result):
                            # 检查cv_points字段，如果为TRUE则进行截屏
                            if data.cv_points and str(data.cv_points).upper() == "TRUE":
                                try:
                                    # 生成截屏文件名
                                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                                    active_screenshot_path = f"Proactive_screenshot_{data.test_case_id}_{timestamp}.png"

                                    # 等待机器人运动完成（关键修复：确保在正确时机截屏）
                                    print("⏳ 等待系统加载完成...")
                                    time.sleep(3)  # 等待3秒让机器人完成运动

                                    # 1、====== 异步调用AI对比图片（主动截屏） ======
                                    opencv_screenshot(active_screenshot_path, self.driver)

                                    Context_Helper.async_ai_comparison(active_screenshot_path)

                                except Exception as screenshot_error:
                                    print(f"❌ 主动截屏失败：{str(screenshot_error)}")

                            logger.info(f"断言成功，测试结果汇总：步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                            # print(f"步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                            print("=" * 50 + "\n")

                        else:
                            try:
                                data.status = "FAIL"
                                data.outputed_result = f"断言失败：预期元素 {data.expected_result} 不可见"
                                print(f"断言失败准备截屏...")

                                # 2、====== 异步调用AI图片对比分析（断言失败,需要需要上下文） ======
                                # 断言失败截屏文件名
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                assertfail_screenshot_name = f"AssertFailed_screenshot_{data.test_case_id}_{timestamp}.png"

                                # 调用截屏方法
                                opencv_screenshot(assertfail_screenshot_name, self.driver)

                                # 调用异步ai分析图片断言失败原因（断言失败需要需要上下文）
                                Context_Helper.async_ai_comparison(screenshot_path=assertfail_screenshot_name,
                                                                   current_data=data,
                                                                   test_data_list=context_data_list)
                            except Exception as screenshot_error:
                                print(f"❌ 断言截屏失败：{str(screenshot_error)}")

                except Exception as e:
                    logger.info(f"执行过程中发生异常: {str(e)}")
                    # 发生异常时也执行下一次循环
                    continue

            # 收集测试结果 - 无论成功失败都记录，使用 execute_step 设置的状态
            # 同时收集点击失败日志和断言日志
            click_logs = ""
            assert_logs = ""
            ai_analysis_result = ""

            if data.status != "PASS":
                click_logs = f"执行失败日志：步骤 {data.step_id} - {data.outputed_result}"

                # 等待AI分析文件生成完成
                max_wait_time = 30  # 最大等待时间
                wait_interval = 0.5  # 每次检测间隔
                waited_time = 0

                # 构建 AI 分析结果文件名模式
                ai_result_pattern = f"ai_comparison_results/AssertFailed_{self.current_sheet}_{data.test_case_id}_*_ai_result.txt"

                try:
                    while waited_time < max_wait_time:

                        ai_files = glob.glob(ai_result_pattern)

                        if ai_files:
                            # 按修改时间排序，获取最新文件
                            ai_files.sort(key=os.path.getmtime, reverse=True)
                            newest_file = ai_files[0]

                            # 文件存在但可能未写完 → 检查文件大小
                            if os.path.getsize(newest_file) > 0:
                                # 文件写入完成 → 读取内容
                                with open(newest_file, 'r', encoding='utf-8') as f:
                                    ai_analysis_result = f.read()
                                break

                        # 若文件不存在或为空 → 等待
                        time.sleep(wait_interval)
                        waited_time += wait_interval

                    # 超时仍未获取结果
                    if not ai_analysis_result:
                        ai_analysis_result = f"AI分析文件生成超时（等待 {max_wait_time} 秒仍未生成有效文件）"

                except Exception as e:
                    ai_analysis_result = f"读取AI分析结果失败: {str(e)}"

            # 无论状态如何都收集断言日志
            assert_logs = f"断言日志：步骤 {data.step_id} - 预期：{data.expected_result}，实际结果：{data.outputed_result}"

            # 查找对应的截图文件
            screenshot_pattern = f"screenshoot_dir/AssertFailed_{self.current_sheet}_{data.test_case_id}_*.png"
            screenshot_files = glob.glob(screenshot_pattern)

            screenshot_base64 = ""  # 初始化变量
            # 1. 将Base64图片数据从assert_logs移到attachments中
            if screenshot_files:
                screenshot_files.sort(key=os.path.getmtime, reverse=True)
                latest_screenshot = screenshot_files[0]

                try:
                    with open(latest_screenshot, 'rb') as f:
                        screenshot_data = f.read()
                        screenshot_base64 = base64.b64encode(screenshot_data).decode('utf-8')

                except Exception as e:
                    print(f"截图读取失败：{str(e)}")

            self.test_results.append(
                {
                    "test_case_id": data.test_case_id,
                    "description": data.description,
                    "status": data.status,  # 使用 execute_step 设置的 status
                    "sheet_name": self.current_sheet,
                    "click_logs": click_logs,  # 点击失败日志
                    "assert_logs": assert_logs,  # 断言日志
                    "AI_analysis": ai_analysis_result,
                    "screenshot_base64":screenshot_base64
                }
            )

        # # 发送测试结果到钉钉
        # bot = AEUIBot()
        # bot.send_test_results(self.test_results, sheet_name=current_sheet)
        # 返回测试结果
        return self.test_results






