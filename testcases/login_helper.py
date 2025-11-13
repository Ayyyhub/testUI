import sys
import pytest
# print("当前使用的Python解释器路径：", sys.executable)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from Log.logger import logger  # 导入封装好的 logger
from utils.conf_reader import load_config
from utils.wait_clickable import wait_overlays_gone



class Login_Helper:

    # def get_available_accounts(self):
    #     """账号生成器，按顺序提供可用账号"""
    #     config = load_config()
    #
    #     # 定义账号池，可以在这里添加更多备用账号
    #     accounts = [
    #         {
    #             'username': config['test_user']['username'],
    #             'password': config['test_user']['password']
    #         }
    #     ]
    #
    #     for account in accounts:
    #         yield account
    def get_available_accounts(self):
        """账号生成器，按顺序提供可用账号"""
        config = load_config()

        # 直接从配置中获取账号列表
        # config['test_user'] 已经是一个包含多个账号字典的列表
        accounts = config['test_user']

        for account in accounts:
            yield account

    def try_login_with_account(self, driver, username, password):
        """尝试使用指定账号登录"""
        try:
            driver.get("http://10.20.220.251/login")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # 输入用户名
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
                username_field.clear()
                username_field.send_keys(username)
            else:
                inputs = driver.find_elements(By.TAG_NAME, "input")
                for input_field in inputs:
                    if input_field.get_attribute("type") in ["text", "email"]:
                        username_field = input_field
                        username_field.clear()
                        username_field.send_keys(username)
                        break

            # 输入密码
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
                password_field.clear()
                password_field.send_keys(password)
            else:
                inputs = driver.find_elements(By.TAG_NAME, "input")
                for input_field in inputs:
                    if input_field.get_attribute("type") == "password":
                        password_field = input_field
                        password_field.clear()
                        password_field.send_keys(password)
                        break

            # 勾选同意并点击登录
            checkbox = driver.find_element(By.CLASS_NAME, "el-checkbox__input")
            checkbox.click()

            denglu_button = driver.find_element(By.CLASS_NAME, "login_btn")
            denglu_button.click()

            # 等待登录结果
            time.sleep(3)

            # 检查是否登录成功
            if driver.current_url == "http://10.20.220.251/homePage":
                logger.info(f"登录成功 - 用户名: {username}")
                time.sleep(2)
                wait_overlays_gone(driver, timeout=10)
                return True
            else:
                logger.info(f"登录失败 - 用户名: {username}, 当前URL: {driver.current_url}")
                return False

        except Exception as e:
            logger.info(f"登录过程中发生错误: {str(e)}")
            return False

    def login_func(self, driver):
        """使用生成器的主登录函数"""
        self.driver = driver
        logger.info("=== 开始执行登录测试 ===")

        # 创建账号生成器
        account_generator = self.get_available_accounts()

        success = False
        max_retries = 3  # 最大重试次数

        for attempt in range(max_retries):
            try:
                account = next(account_generator)
                username = account['username']
                password = account['password']

                logger.info(f"尝试使用账号登录: {username} (尝试 {attempt + 1}/{max_retries})")

                success = self.try_login_with_account(driver, username, password)

                if success:
                    break
                else:
                    logger.info(f"账号 {username} 登录失败，尝试下一个账号...")
                    # 可以在这里添加清除登录状态的逻辑（如果需要）
                    # self.logout_if_needed(driver)

            except StopIteration:
                logger.info("所有账号都已尝试，没有可用的账号")
                break
            except Exception as e:
                logger.error(f"登录过程中发生异常: {str(e)}")  # 改为 error 级别
                continue

        if not success:
            logger.error("所有登录尝试都失败了")
        else:
            logger.info("登录流程完成")

        return success


