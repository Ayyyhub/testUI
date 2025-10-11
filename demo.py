from telnetlib import EC

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import driver
from core.browser_engine import BrowserEngine
from core.execute_test_data import UITestExecutor
from core.logger import logger
from utils.conf_reader import load_config
from utils.excell_reader import Excellreader
import time

def truework01_func1():
    s=BrowserEngine()
    driver1=s.initialize_driver()


    config = load_config()
    excell_path = config['excell_path']
    excell_reader = Excellreader(excell_path)

    # 获取用户名和密码
    username = config['test_user']['username'] if config else "AE11"  # 默认值作为备份
    password = config['test_user']['password'] if config else "JfrnUJ.34k"  # 默认值作为备份

    try:
        # 打开登录页面
        driver1.get("http://10.20.220.251/login")

        # 等待页面加载完成
        WebDriverWait(driver1, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 查找用户名输入框并输入用户名
        # 根据实际页面调整选择器，这里使用常见的几种选择器尝试
        username_selectors = [
            "input[type='text']",
            "input[name='username']",
            "#username",
            ".username"
        ]

        username_field = None
        for selector in username_selectors:
            try:
                username_field = driver1.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue

        if username_field:
            username_field.send_keys(username)
        else:
            # 如果常见选择器都找不到，尝试找到所有输入框并使用第一个
            inputs = driver1.find_elements(By.TAG_NAME, "input")
            for input_field in inputs:
                if input_field.get_attribute("type") in ["text", "email"]:
                    username_field = input_field
                    username_field.send_keys(username)
                    break

        # 查找密码输入框并输入密码
        password_selectors = [
            "input[type='password']",
            "input[name='password']",
            "#password",
            ".password"
        ]

        password_field = None
        for selector in password_selectors:
            try:
                password_field = driver1.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue

        if password_field:
            password_field.send_keys(password)
        else:
            # 如果常见选择器都找不到，尝试找到所有输入框并使用密码类型的
            inputs = driver1.find_elements(By.TAG_NAME, "input")
            for input_field in inputs:
                if input_field.get_attribute("type") == "password":
                    password_field = input_field
                    password_field.send_keys(password)
                    break

        # 勾选已同意
        checkbox = driver1.find_element(By.CLASS_NAME, "el-checkbox__input")
        checkbox.click()

        # 查找登录按钮并点击
        denglu_button = driver1.find_element(By.CLASS_NAME, "login_btn")
        denglu_button.click()

        time.sleep(3)

        # 在for循环中添加更详细的错误处理
        test_data_list2 = excell_reader.get_test_data(sheet_name="workflow01")
        for data in test_data_list2:
            if data:
                try:
                    print(f"\n开始执行测试用例：{data.step_id}")
                    execute = UITestExecutor(driver1)
                    time.sleep(2)
                    execute.execute_step(data)

                    print("测试结果汇总:")
                    print(f"步骤 {data.step_id}: {data.status} - {data.outputed_result}\n")
                except Exception as e:
                    print(f"执行步骤 {data.step_id} 时发生错误: {str(e)}")
    except Exception as e:
        print("发生错误:", str(e))

if __name__ == '__main__':
    truework01_func1()