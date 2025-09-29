# base_test.py
from logging import exception
from warnings import catch_warnings
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BaseTest:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)

    def teardown_method(self):
        self.driver.quit()

    @fixtures
    def login(self, username: str, password: str):
        """登录操作"""
        self.driver.get("https://testerhome.com/")

        # 显式等待元素可点击（最长等待10秒）
        login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-primary.btn-jumbotron.btn-lg"))
        )
        # 点击登录按钮
        login_button.click()
        # 定位元素
        username_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "user_login"))
        )
        # 清空输入框（可选，根据实际需求）
        username_input.clear()
        # 设置输入框值为'ay'
        username_input.send_keys(username)

        password_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "user_password"))
        )
        # 清空输入框（可选，根据实际需求）
        password_input.clear()
        # 设置输入框值为'ay'
        password_input.send_keys(password)
        from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException

        try:
            # 定位“记住登录状态”的label元素（通过for属性关联复选框）
            remember_label = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "label.custom-control-label[for='user_remember_me']")
                )
            )

            # 点击label触发复选框选中
            remember_label.click()
            print("已通过label触发“记住登录状态”复选框选中")
        except TimeoutException:
            print("超时错误：未在10秒内找到'记住登录状态'复选框")
        except NoSuchElementException:
            print("元素未找到：页面中不存在id为user_remember_me的复选框")
        except ElementNotInteractableException:
            print("元素不可交互：'记住登录状态'复选框存在但无法点击")
        except Exception as e:
            print(f"点击复选框时发生未知错误：{str(e)}")
        # 执行登录
        login_button1 = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "form-actions"))
        )
        # 点击登录按钮
        login_button1.click()


        time.sleep(3)

    def get_login_result(self) -> str:
        """获取登录结果 - 修复版"""
        try:
            # 等待页面稳定
            time.sleep(3)
            url="https://testerhome.com/"
            current_url = self.driver.current_url
            page_title = self.driver.title
            print(f"登录后URL: {current_url}")
            print(f"登录后标题: {page_title}")

            # # 根据URL和页面内容判断登录结果
            # if "login" in current_url or "sign_in" in current_url:
            #     # 如果还在登录页面，说明登录失败
            #     # 查找错误信息
            #     error_selectors = [
            #         ".alert-error",
            #         ".error",
            #         ".flash-error",
            #         "[class*='error']",
            #         "[class*='alert']",
            #         ".text-danger"
            #     ]
            #
            #     for selector in error_selectors:
            #         try:
            #             error_element = self.driver.find_element(By.CSS_SELECTOR, selector)
            #             if error_element.is_displayed():
            #                 error_text = error_element.text
            #                 if error_text:
            #                     return f"登录失败: {error_text}"
            #         except:
            #             continue
            #
            #     return "登录失败，但未找到具体错误信息"
            # else:
            #     # 不在登录页面，可能登录成功
            #     # 检查是否有用户相关的元素
            #     user_indicators = [
            #         "[href*='logout']",
            #         "[href*='profile']",
            #         ".user-info",
            #         ".avatar",
            #         ".user-name"
            #     ]
            #
            #     for indicator in user_indicators:
            #         try:
            #             user_element = self.driver.find_element(By.CSS_SELECTOR, indicator)
            #             if user_element.is_displayed():
            #                 return "登录成功"
            #         except:
            #             continue
            #
            #     # 如果没有找到用户元素，但已离开登录页，也认为是成功
            #     return "登录可能成功（已离开登录页面）"
            if url==current_url:
                print("登录成功")
                return "登录成功"
        except Exception as e:
            return f"检查登录结果时发生错误: {str(e)}"