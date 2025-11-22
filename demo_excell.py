from clean_specified_dir import cleanup_directories
from qwen_compare.context_helper import Context_Helper
# from AEUI_Bot import AEUIBot
# from conftest import driver
from core.browser_engine import BrowserEngine
from core.execute_test_data import UITestExecutor
from qwen_compare.opencv import opencv_screenshot
from testcases.login_helper import LoginHelper
from utils.conf_reader import load_config
from utils.excell_reader import Excellreader
import time
from core.assertion import customed_assertion


class demo:
    def __init__(self):
        self.test_results = []  # 用于存储测试结果
        self.current_sheet = "demo"  # 当前使用的sheet页名称


    def truework01_func1(self):
        s = BrowserEngine()
        driver1 = s.initialize_driver()

        cleanup_directories()

        # 1. 执行登录测试
        test_login_example = LoginHelper()
        test_login_example.login_func(driver1)

        time.sleep(3)

        config = load_config()
        excell_path = config['excell_path']
        cs_assert = customed_assertion(driver1)
        excell_reader = Excellreader(excell_path)
        demo_test_data_list = excell_reader.get_test_data(sheet_name="demo")
        for data in demo_test_data_list:
            # 写个”滑块算法“优化一下------get_context_data
            context_data_list = Context_Helper.get_context_data(data, demo_test_data_list, 2)
            if data:
                try:
                    print(f"\n开始执行测试用例：{data.step_id}")
                    print(f"步骤描述: {data.description}")

                    # 执行测试步骤
                    execute = UITestExecutor(driver1)
                    execute.execute_step(data)

                    if data.assert_type=="visible":
                        # 进行断言检查（传递上下文信息）
                        if cs_assert.assert_element_visible(data.assert_method,data.expected_result):
                            # 断言成功 - 继续执行后续代码

                            # 检查cv_points字段，如果为TRUE则进行截屏
                            if data.cv_points and str(data.cv_points).upper() == "TRUE":
                                try:
                                    # 生成截屏文件名
                                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                                    active_screenshot_path = f"Proactive_screenshot_{data.test_case_id}_{timestamp}.png"

                                    # 等待机器人运动完成（关键修复：确保在正确时机截屏）
                                    print("⏳ 等待系统加载完成...")
                                    time.sleep(3)  # 等待3秒让机器人完成运动

                                    # 1、====== 异步调用AI对比图片（主动截屏不需要上下文） ======
                                    opencv_screenshot(active_screenshot_path, driver1)

                                    Context_Helper.async_ai_comparison(active_screenshot_path)

                                except Exception as screenshot_error:
                                    print(f"❌ 主动截屏失败：{str(screenshot_error)}")

                            print(f"断言成功，测试结果汇总：步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                            # print(f"步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                            print("=" * 50 + "\n")

                        else:
                            try:
                                # 断言失败

                                data.status = "FAIL"
                                data.outputed_result = f"断言失败：预期元素 {data.expected_result} 不可见"
                                print(f"断言失败准备截屏...")

                                # 2、====== 异步调用AI图片对比分析（断言失败需要需要上下文） ======
                                # 断言失败截屏文件名
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                assertfail_screenshot_name = f"AssertFailed_screenshot_{data.test_case_id}_{timestamp}.png"

                                # 调用截屏方法
                                opencv_screenshot(assertfail_screenshot_name, driver1)

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

                                    # 1、====== 异步调用AI对比图片（主动截屏不需要上下文） ======
                                    opencv_screenshot(active_screenshot_path, driver1)

                                    Context_Helper.async_ai_comparison(active_screenshot_path)

                                except Exception as screenshot_error:
                                    print(f"❌ 主动截屏失败：{str(screenshot_error)}")

                            print(f"断言成功，测试结果汇总：步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                            # print(f"步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                            print("=" * 50 + "\n")

                        else:
                            try:
                                # 断言失败

                                data.status = "FAIL"
                                data.outputed_result = f"断言失败：预期元素 {data.expected_result} 不可见"
                                print(f"断言失败准备截屏...")

                                # 2、====== 异步调用AI图片对比分析（断言失败需要需要上下文） ======
                                # 断言失败截屏文件名
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                assertfail_screenshot_name = f"AssertFailed_screenshot_{data.test_case_id}_{timestamp}.png"

                                # 调用截屏方法
                                opencv_screenshot(assertfail_screenshot_name, driver1)

                                # 调用异步ai分析图片断言失败原因（断言失败需要需要上下文）
                                Context_Helper.async_ai_comparison(screenshot_path=assertfail_screenshot_name,
                                                                   current_data=data,
                                                                   test_data_list=context_data_list)
                            except Exception as screenshot_error:
                                print(f"❌ 断言截屏失败：{str(screenshot_error)}")

                except Exception as e:
                    print(f"for循环，步入执行过程中发生异常: {str(e)}")
                    # 发生异常时也执行下一次循环
                    continue

            # 收集测试结果 - 无论成功失败都记录，使用 execute_step 设置的状态
            self.test_results.append({
                'test_case_id': data.test_case_id,
                'description': data.description,
                'status': data.status,  # 使用 execute_step 设置的 status
            })


if __name__ == '__main__':
    a = demo()
    a.truework01_func1()













