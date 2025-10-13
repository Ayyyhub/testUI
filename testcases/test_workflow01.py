import pytest
from selenium.webdriver import ActionChains

from core.execute_test_data import UITestExecutor
from testcases.test_upload import aTest_upload
from utils.conf_reader import load_config
from utils.excell_reader import Excellreader
from core.logger import logger


class Test_truework01:

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
            pytest.fail("上传失败，跳过工作流程测试")

        logger.info("=== 开始执行work_flow01 ===")
        self.driver = driver  # 保存driver到实例，后续用self.driver,如果后续有其他方法在同一个类下，无需再传 driver 参数
        actions = ActionChains(driver)
        config = load_config()
        excell_path = config['excell_path']
        excell_reader = Excellreader(excell_path)
        test_data_list2=excell_reader.get_test_data(sheet_name="workflow01")
        for data in test_data_list2:
            if data:
                print(f"\n执行测试用例：{data}")
                execute = UITestExecutor(driver,actions)
                execute.execute_step(data)
                print("测试结果汇总:")
                print(f"步骤 {data.step_id}: {data.status} - {data.outputed_result}\n")




