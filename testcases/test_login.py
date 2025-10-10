import sys

import pytest
# print("当前使用的Python解释器路径：", sys.executable)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from core.logger import logger  # 导入封装好的 logger
from utils.conf_reader import load_config




class Test_login:

    # @pytest.mark.dependency(name="login")
    @pytest.mark.run(order=1)
    def test_login_func(self,driver):
        self.driver = driver  # 保存driver到实例，后续用self.driver,如果后续有其他方法在同一个类下，无需再传 driver 参数
        logger.info("=== 开始执行登录测试 ===")

        # 加载配置
        config = load_config()

        # 获取用户名和密码
        username = config['test_user']['username'] if config else "AE11"  # 默认值作为备份
        password = config['test_user']['password'] if config else "JfrnUJ.34k"  # 默认值作为备份


        try:
            # 打开登录页面
            driver.get("http://10.20.220.251/login")

            # 等待页面加载完成
            WebDriverWait(driver, 10).until(
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
                    username_field = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue

            if username_field:
                username_field.send_keys(username)
            else:
                # 如果常见选择器都找不到，尝试找到所有输入框并使用第一个
                inputs = driver.find_elements(By.TAG_NAME, "input")
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
                    password_field = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue

            if password_field:
                password_field.send_keys(password)
            else:
                # 如果常见选择器都找不到，尝试找到所有输入框并使用密码类型的
                inputs = driver.find_elements(By.TAG_NAME, "input")
                for input_field in inputs:
                    if input_field.get_attribute("type") == "password":
                        password_field = input_field
                        password_field.send_keys(password)
                        break

            # 勾选已同意
            checkbox = driver.find_element(By.CLASS_NAME, "el-checkbox__input")
            checkbox.click()

            # 查找登录按钮并点击
            denglu_button=driver.find_element(By.CLASS_NAME, "login_btn")
            denglu_button.click()

            # 等待登录完成
            time.sleep(3)
            if driver.current_url == "http://10.20.220.251/homePage":
                # 等待页面加载完成
                # print("登录成功，等待页面加载...")
                logger.info("登录成功，等待页面加载...")
                time.sleep(2)  # 给页面一些时间加载

            else:
                print("页面加载异常，URL:", driver.current_url)



        except Exception as e:
            print("发生错误:", str(e))

