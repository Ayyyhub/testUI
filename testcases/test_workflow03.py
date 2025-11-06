from core.assertion import customed_assertion
from core.execute_test_data import UITestExecutor
from testcases.login_helper import Login_Helper
from testcases.newcreate_helper import NewcreateHelper
from Log.logger import logger
from utils.conf_reader import load_config
from utils.excell_reader import Excellreader
import pytest

class Test_truework03:

    def test_truework03_func(self,driver):
        self.test_results = []
        self.current_sheet = "路径生成程序"
        # 1. 执行登录测试
        test_login_example = Login_Helper()
        test_login_example.login_func(driver)
        # 点击新建
        new_create = NewcreateHelper()
        new_create.newcreate_func(driver)
        logger.info("=== 开始执行work_flow03 ===")
        self.driver = driver  # 保存driver到实例，后续用self.driver,如果后续有其他方法在同一个类下，无需再传 driver 参数
        # actions = ActionChains(driver)
        config = load_config()
        excell_path = config['excell_path']
        excell_reader = Excellreader(excell_path)
        current_sheet = "路径生成程序"
        test_data_list3 = excell_reader.get_test_data(sheet_name=current_sheet)
        cs_assert = customed_assertion(driver)

        for data in test_data_list3:
            if data:
                print("\n" + "="*50)  # 添加分隔线
                print(f"执行测试用例：{data}")
                
                # monitor.start()
                try:
                    # 执行excell元素流程测试
                    execute = UITestExecutor(driver)

                    execute.execute_step(data)

                    # 进行断言检查
                    if cs_assert.assert_element_visible(data.expected_result):
                        # 断言成功 - 继续执行后续代码
                        print("断言成功，操作结束，测试结果汇总:")
                        print(f"步骤 {data.step_id}: {data.status} - {data.outputed_result}")
                        print("=" * 50 + "\n")
                    else:
                        # 断言失败 - 跳过后续操作，执行下一个测试用例
                        print(f"断言失败，跳过后续操作，执行下一个测试用例")
                        data.status = "FAIL"
                        data.outputed_result = f"断言失败：预期元素 {data.expected_result} 不可见"

                except Exception as e:
                    print(f"执行过程中发生异常: {str(e)}")
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