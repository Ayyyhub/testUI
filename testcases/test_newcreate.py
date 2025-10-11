# import pytest
# from core.logger import logger
# from pages.base_page import BasePase
# from core.execute_test_data import UITestExecutor
# from utils.excell_reader import Excellreader
# # from basepage import BaseTest
# from utils.conf_reader import load_config
#
# class Test_NewCreate:
#
#     # @pytest.mark.parametrize("test_data", [
#     #     pytest.param(data, id=data.test_case_id)
#     #     for data in Excellreader(excell_path).get_test_data(sheet_name="newcreate")
#     # ])
#     # def test_newcreate_func1(self,test_data: AETestData, driver):
#     #
#     #     """数据驱动登录测试"""
#     #     if not test_data:
#     #         print("未找到可执行的测试用例")
#     #         #exit() # 用return而非exit()，避免终止整个测试进程
#     #         return
#     #
#     #     print(f"执行测试用例:{test_data.description}")
#     #     # 3. 执行测试步骤
#     #     executor = UITestExecutor(driver)
#     #     for step in test_data:
#     #         executor.execute_step(step)
#     #     print("\n测试结果汇总:")
#     #     for step in test_data:
#     #         print(f"步骤 {step.step_id}: {step.status} - {step.outputed_result}")
#
#     # @pytest.mark.dependency(depends=["login"],name="newcreate")
#     @pytest.mark.run(order=2)
#     def test_newcreate_func(self, driver):
#         logger.info("=== 开始执行点击新建场景 ===")
#         self.driver = driver  # 保存driver到实例，后续用self.driver,如果后续有其他方法在同一个类下，无需再传 driver 参数
#
#         config = load_config()
#         excell_path = config['excell_path']
#         excell_reader = Excellreader(excell_path)
#         test_data_list = excell_reader.get_test_data(sheet_name="newcreate")
#         for test_data in test_data_list:
#             if test_data:
#                 print(f"执行测试用例: {test_data.description}")
#                 # 直接调用测试逻辑，复用test_new_create_func中的代码
#                 executor = UITestExecutor(driver)
#
#                 executor.execute_step(test_data)
#
#                 # 断言
#                 basepage = BasePase(driver=self.driver)
#                 tab_info = basepage.get_xinjianNum()
#
#                 if tab_info['count'] == test_data.expected_result:
#                     print("与预期结果一致")
#                     logger.info("与预期结果一致")
#                     test_data.status = "PASS"
#                 else:
#                     test_data.status = "FAIL"
#
#                 print("\n测试结果汇总:")
#                 print(f"步骤 {test_data.step_id}: {test_data.status} - {test_data.outputed_result}")
#
