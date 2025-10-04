import os

import pytest
from selenium.webdriver.common.by import By

from pages.read_test_data import UITestExecutor
from utils.conf_reader import load_config
from utils.excell_reader import Excellreader, TestData

class Test_truework01:

    # @pytest.mark.parametrize("test_data", [
    #     pytest.param(data, id=data.test_case_id)
    #     for data in Excellreader(excell_path).get_test_data(sheet_name="truework")
    # ])
    def test_truework01_func(self,driver):
        config = load_config()
        excell_path = config['excell_path']
        test_data_list2=Excellreader.get_test_data(sheet_name="truework")
        for data in test_data_list2:
            if data:
                print(f"执行测试用例：{data}")
                execute = UITestExecutor(driver)
                execute.execute_step(data)
                print("\n测试结果汇总:")
                print(f"步骤 {data.step_id}: {data.status} - {data.outputed_result}")




