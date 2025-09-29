# test_login.py
import pytest
from utils.excell_reader import Excellreader, TestData
from basepage1 import BaseTest


class TestLogin(BaseTest):

    @pytest.mark.parametrize("test_data", [
        pytest.param(data, id=data.test_case_id)
        for data in Excellreader("test_data.xlsx").get_test_data()
    ])
    def test_login_scenarios(self, test_data: TestData):
        """数据驱动登录测试"""
        print(f"执行测试用例: {test_data.description}")

        # 执行登录
        self.login(test_data.username, test_data.password)

        # 验证结果
        actual_result = self.get_login_result()
        expected_result = test_data.expected_result

        # 断言
        assert expected_result in actual_result, (
            f"测试失败: 期望 '{expected_result}', 实际 '{actual_result}'"
        )

        # 记录结果（可选）
        self.record_test_result(test_data.test_case_id, actual_result, "PASS")

    def record_test_result(self, test_case_id: str, actual_result: str, status: str):
        """记录测试结果"""
        excel_reader = Excellreader("test_data.xlsx")
        excel_reader.write_result(test_case_id, actual_result, status)