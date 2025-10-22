import pytest
from selenium.webdriver import ActionChains

from AEUI_Bot import AEUIBot
from core.execute_test_data import UITestExecutor
from testcases.test_upload import aTest_upload
from utils.conf_reader import load_config
from utils.excell_reader import Excellreader
from Log.logger import logger
from utils.perfomance.performance_monit import PerformanceMonitor


class Test_truework01:

    def __init__(self):
        self.test_results = []  # 用于存储测试结果
        self.current_sheet = "workflow01"  # 当前使用的sheet页名称

    # @pytest.mark.parametrize("test_data", [
    #     pytest.param(data, id=data.test_case_id)
    #     for data in Excellreader(excell_path).get_test_data(sheet_name="truework")
    # ])
    # @pytest.mark.dependency(depends=["upload"])
    @pytest.mark.run(order=2)
    def test_truework01_func(self,driver):
        # 1. 执行上传
        upload_test = aTest_upload()
        upload_result = upload_test.atest_upload(driver)

        # 2. 确保上传成功后再执行工作流程
        if upload_result:
            logger.info("上传成功，开始执行工作流程")
            # 删除递归调用，直接执行工作流程逻辑
        else:
            logger.error("上传失败，跳过工作流程测试")

        logger.info("=== 开始执行work_flow01 ===")
        self.driver = driver  # 保存driver到实例，后续用self.driver,如果后续有其他方法在同一个类下，无需再传 driver 参数
        # actions = ActionChains(driver)
        config = load_config()
        excell_path = config['excell_path']
        excell_reader = Excellreader(excell_path)
        current_sheet="workflow01"
        test_data_list2=excell_reader.get_test_data(sheet_name=current_sheet)
        # monitor = PerformanceMonitor("workflow01")
        for data in test_data_list2:
            if data:
                print("\n" + "="*50)  # 添加分隔线
                print(f"执行测试用例：{data}")
                # 执行excell元素流程测试
                # monitor.start()
                execute = UITestExecutor(driver)
                execute.execute_step(data)
                # monitor.checkpoint(f"checkpoint步骤{data.step_id}-{data.description}")
                print("测试结果汇总:")
                print(f"步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                print("="*50 + "\n")  # 添加分隔线

        # 结束监控并输出报告级别日志（可调整阈值）
        # monitor.stop(warn_threshold=15000, error_threshold=30000)

                # 收集测试结果
                self.test_results.append({
                    'test_case_id': data.test_case_id,
                    'description': data.description,
                    'status': data.status,

                })

        # 发送测试结果到钉钉
        bot = AEUIBot()
        bot.send_test_results(self.test_results, sheet_name=current_sheet)




