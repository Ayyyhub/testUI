from testcases.newcreate_helper import NewcreateHelper

from conftest import driver
from context_helper import Context_Helper

from core.execute_test_data import UITestExecutor
from Log.logger import logger
from image_comparison import ImageComparison
from opencv import opencv_screenshot
from testcases.login_helper import LoginHelper
from utils import excell_reader
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
        self.current_sheet = "路径生成程序"
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
            context_data_list = Context_Helper.get_context_data(data, test_data_list3, 2)
            if data:
                print("=" * 50)
                logger.info(f"执行测试用例：{data}")

                # monitor.start()
                try:
                    # 执行excell元素流程测试
                    execute = UITestExecutor(self.driver)
                    execute.execute_step(data)

                    if data.assert_type == "visible":
                        # 进行断言检查（传递上下文信息）
                        if cs_assert.assert_element_visible(data.assert_method, data.expected_result):
                            # 断言成功

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
                                    opencv_screenshot(active_screenshot_path, self.driver)

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

                                    # 1、====== 异步调用AI对比图片（主动截屏不需要上下文） ======
                                    opencv_screenshot(active_screenshot_path, self.driver)

                                    Context_Helper.async_ai_comparison(active_screenshot_path)

                                except Exception as screenshot_error:
                                    print(f"❌ 主动截屏失败：{str(screenshot_error)}")

                            print(f"断言成功，测试结果汇总：步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                            # print(f"步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                            print("=" * 50 + "\n")

                        else:
                            try:
                                data.status = "FAIL"
                                data.outputed_result = f"断言失败：预期元素 {data.expected_result} 不可见"
                                print(f"断言失败准备截屏...")

                                # 2、====== 异步调用AI图片对比分析（断言失败需要需要上下文） ======
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
            self.test_results.append(
                {
                    "test_case_id": data.test_case_id,
                    "description": data.description,
                    "status": data.status,  # 使用 execute_step 设置的 status
                    "sheet_name": self.current_sheet,
                }
            )

        # # 发送测试结果到钉钉
        # bot = AEUIBot()
        # bot.send_test_results(self.test_results, sheet_name=current_sheet)
        # 返回测试结果
        return self.test_results
