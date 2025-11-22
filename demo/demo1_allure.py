
import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.browser_engine import BrowserEngine
from core.assertion import customed_assertion
from core.execute_test_data import UITestExecutor
from Log.logger import logger
from utils.conf_reader import load_config
from utils.excell_reader import Excellreader
import time

class TestDemo:
    """Demo测试类 - 用于生成Allure测试报告"""

    def setup_method(self):
        """每个测试方法前的初始化"""
        self.browser_engine = BrowserEngine()
        self.driver = self.browser_engine.initialize_driver()
        self.config = load_config()
        self.excell_path = self.config['excell_path']
        self.excell_reader = Excellreader(self.excell_path)
        self.current_sheet = "demo"
        self.test_results = []

    def teardown_method(self):
        """每个测试方法后的清理"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()

    @allure.feature("Demo测试")
    @allure.story("完整的Demo工作流程测试")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_demo_workflow(self):
        """测试Demo工作流程"""
        with allure.step("步骤1: 用户登录"):
            self._login()

        with allure.step("步骤2: 执行Excel中的测试用例"):
            self._execute_test_cases()

        with allure.step("步骤3: 验证测试结果"):
            self._verify_results()

    def _login(self):
        """登录功能"""
        username = self.config['test_user']['username'] if self.config else "AE11"
        password = self.config['test_user']['password'] if self.config else "JfrnUJ.34k"

        with allure.step("打开登录页面"):
            self.driver.get("http://10.20.220.251/login")
            allure.attach(self.driver.get_screenshot_as_png(), name="登录页面",
                          attachment_type=allure.attachment_type.PNG)

        with allure.step("等待页面加载"):
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

        with allure.step("输入用户名"):
            username_field = self._find_username_field()
            username_field.clear()
            username_field.send_keys(username)
            allure.attach(f"输入的用户名: {username}", name="用户名输入")

        with allure.step("输入密码"):
            password_field = self._find_password_field()
            password_field.clear()
            password_field.send_keys(password)
            allure.attach("密码已输入", name="密码输入")

        with allure.step("勾选同意协议"):
            checkbox = self.driver.find_element(By.CLASS_NAME, "el-checkbox__input")
            if not checkbox.is_selected():
                checkbox.click()

        with allure.step("点击登录按钮"):
            login_button = self.driver.find_element(By.CLASS_NAME, "login_btn")
            login_button.click()
            allure.attach(self.driver.get_screenshot_as_png(), name="登录后页面",
                          attachment_type=allure.attachment_type.PNG)

        time.sleep(3)

    def _find_username_field(self):
        """查找用户名输入框"""
        username_selectors = [
            "input[type='text']",
            "input[name='username']",
            "#username",
            ".username"
        ]

        for selector in username_selectors:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element.is_displayed() and element.is_enabled():
                    return element
            except:
                continue

        # 如果常见选择器都找不到，尝试找到所有输入框并使用第一个
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        for input_field in inputs:
            if input_field.get_attribute("type") in ["text", "email"]:
                if input_field.is_displayed() and input_field.is_enabled():
                    return input_field

        raise Exception("未找到用户名输入框")

    def _find_password_field(self):
        """查找密码输入框"""
        password_selectors = [
            "input[type='password']",
            "input[name='password']",
            "#password",
            ".password"
        ]

        for selector in password_selectors:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element.is_displayed() and element.is_enabled():
                    return element
            except:
                continue

        # 如果常见选择器都找不到，尝试找到所有输入框并使用密码类型的
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        for input_field in inputs:
            if input_field.get_attribute("type") == "password":
                if input_field.is_displayed() and input_field.is_enabled():
                    return input_field

        raise Exception("未找到密码输入框")

    def _execute_test_cases(self):
        """执行Excel中的测试用例"""
        cs_assert = customed_assertion(self.driver)
        test_data_list = self.excell_reader.get_test_data(sheet_name="demo")

        for data in test_data_list:
            if data:
                with allure.step(f"执行测试步骤: {data.step_id} - {data.description}"):
                    try:
                        logger.info(f"开始执行测试用例：{data.step_id}")

                        # 在执行前先检查元素是否存在
                        if data.determin_type == "click":
                            try:
                                element = WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, data.determin_value))
                                )
                                logger.info(f"元素状态: 可见={element.is_displayed()}, 启用={element.is_enabled()}")
                            except Exception as e:
                                logger.error(f"元素检查失败: {str(e)}")
                                allure.attach(f"元素检查失败: {str(e)}", name="元素检查")

                        # 执行测试步骤
                        execute = UITestExecutor(self.driver)
                        execute.execute_step(data)

                        # 进行断言检查
                        if cs_assert.assert_element_visible(data.expected_result):
                            data.status = "PASS"
                            allure.attach(f"步骤 {data.step_id}: 断言成功", name="断言结果")
                        else:
                            print(f"断言失败，跳过后续操作，执行下一个测试用例")
                            data.status = "FAIL"
                            data.outputed_result = f"断言失败：预期元素 {data.expected_result} 不可见"
                            allure.attach(f"步骤 {data.step_id}: 断言失败", name="断言结果")

                        # 添加截图
                        allure.attach(self.driver.get_screenshot_as_png(),
                                      name=f"步骤{data.step_id}_结果",
                                      attachment_type=allure.attachment_type.PNG)

                    except Exception as e:
                        logger.error(f"执行过程中发生异常: {str(e)}")
                        data.status = "ERROR"
                        data.outputed_result = f"执行异常: {str(e)}"
                        allure.attach(f"执行异常: {str(e)}", name="异常信息")
                        allure.attach(self.driver.get_screenshot_as_png(),
                                      name=f"步骤{data.step_id}_异常",
                                      attachment_type=allure.attachment_type.PNG)

                # 收集测试结果
                self.test_results.append({
                    'test_case_id': data.test_case_id,
                    'description': data.description,
                    'status': data.status,
                })

    def _verify_results(self):
        """验证测试结果"""
        if not self.test_results:
            pytest.skip("没有测试结果可验证")

        passed_cases = sum(1 for case in self.test_results if case.get('status') == 'PASS')
        total_cases = len(self.test_results)

        with allure.step("统计测试结果"):
            allure.attach(f"总测试用例数: {total_cases}", name="测试统计")
            allure.attach(f"通过用例数: {passed_cases}", name="测试统计")
            if total_cases > 0:
                allure.attach(f"通过率: {(passed_cases / total_cases * 100):.2f}%", name="测试统计")
            else:
                allure.attach("通过率: 0%", name="测试统计")

        # 断言所有测试用例都通过
        assert passed_cases == total_cases, f"测试用例未全部通过，通过率: {(passed_cases / total_cases * 100):.2f}%"


if __name__ == "__main__":
    pytest.main(["-v", "-s", "test.demo1.py", "--alluredir=./allure-results"])


# # 运行测试
# pytest demo1_allure.py -v --alluredir=./allure-results
# pytest testcase/ -v --alluredir=./allure-results
# python main.py -v --alluredir=./allure-results
#
# # 生成报告 -o: output
# allure generate ./allure-results -o ./allure-report --clean
#
# # 打开报告
# allure open ./allure-report