import pytest
from selenium.webdriver import ActionChains

from AEUI_Bot import AEUIBot
from core.assertion import customed_assertion
from core.execute_test_data import UITestExecutor
from testcases.login_helper import Login_Helper
from testcases.upload_helper import UploadHelper
from utils.conf_reader import load_config
from utils.excell_reader import Excellreader
from Log.logger import logger
from utils.perfomance.performance_monit import PerformanceMonitor


class Test_truework01:

    # def setup_method(self):
    # self.test_results = []  # 用于存储测试结果
    # self.current_sheet = "创建工具工作流"  # 当前使用的sheet页名称

    # @pytest.mark.parametrize("test_data", [
    #     pytest.param(data, id=data.test_case_id)
    #     for data in Excellreader(excell_path).get_test_data(sheet_name="truework")
    # ])
    # @pytest.mark.dependency(depends=["upload"])
    # @pytest.mark.run(order=2)
    def test_truework01_func(self, driver):
        self.test_results = []
        self.current_sheet = "创建工具工作流"

        logger.info("=== 调试信息：开始执行test_truework01_func ===")

        # 1. 执行登录测试
        test_login_example = Login_Helper()
        test_login_example.login_func(driver)
        # 1. 执行上传
        upload_test = UploadHelper()
        upload_result = upload_test.upload_model(driver)

        # 2. 确保上传成功后再执行工作流程
        if upload_result:
            logger.info("上传成功，开始执行工作流程")
            # 删除递归调用，直接执行工作流程逻辑
        else:
            logger.error("上传失败，跳过工作流程测试")

        logger.info("=== 开始执行work_flow01 ===" + "\n")
        self.driver = driver  # 保存driver到实例，后续用self.driver,如果后续有其他方法在同一个类下，无需再传 driver 参数
        # actions = ActionChains(driver)
        config = load_config()
        excell_path = config['excell_path']
        excell_reader = Excellreader(excell_path)
        current_sheet = "创建工具工作流"
        test_data_list2 = excell_reader.get_test_data(sheet_name=current_sheet)
        cs_assert = customed_assertion(driver)
        # monitor = PerformanceMonitor("workflow01")
        for data in test_data_list2:
            if data:
                logger.info("=" * 50)
                logger.info(f"执行测试用例：{data}")
                # 执行excell元素流程测试
                # monitor.start()
                try:
                    execute = UITestExecutor(driver)

                    execute.execute_step(data)

                    # 进行断言检查
                    if cs_assert.assert_element_visible(data.expected_result):
                        # 断言成功 - 继续执行后续代码
                        logger.info("断言成功，操作结束，测试结果汇总:")
                        logger.info(
                            f"步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                        logger.info("=" * 50 + "\n")
                    else:
                        # 断言失败
                        logger.info(f"断言失败，跳过后续操作，执行下一个测试用例")
                        data.status = "FAIL"
                        data.outputed_result = f"断言失败：预期元素 {data.expected_result} 不可见"

                except Exception as e:
                    logger.info(f"执行过程中发生异常: {str(e)}")
                    # 发生异常时也执行下一次循环
                    continue

            # 收集测试结果 - 无论成功失败都记录，使用 execute_step 设置的状态
            self.test_results.append({
                'test_case_id': data.test_case_id,
                'description': data.description,
                'status': data.status,  # 使用 execute_step 设置的 status
                'sheet_name': current_sheet,
            })

        # # 发送测试结果到钉钉
        # bot = AEUIBot()
        # bot.send_test_results(self.test_results, sheet_name=current_sheet)
        # 返回测试结果
        return self.test_results
