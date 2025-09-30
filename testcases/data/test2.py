import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import subprocess
import os

from core.browser_engine import BrowserEngine
from core.logger import logger
from utils.conf_reader import load_config

@pytest.fixture
def driver():
    browser_engine = BrowserEngine()
    driver = browser_engine.initialize_driver()
    yield driver
    driver.quit()

# 整个流程合并到一个测试函数中，避免其他 test 开头的函数
def test_full_flow(driver):  # 唯一的测试函数，包含所有步骤
    # 步骤1：登录逻辑（原 test_login_func 的内容）
    config = load_config()
    username = config['test_user']['username'] if config else "AE11"
    password = config['test_user']['password'] if config else "JfrnUJ.34k"

    try:
        driver.get("http://10.20.220.251/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 输入用户名（省略重复代码，保持原逻辑）
        username_selectors = ["input[type='text']", "input[name='username']", "#username", ".username"]
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
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for input_field in inputs:
                if input_field.get_attribute("type") in ["text", "email"]:
                    input_field.send_keys(username)
                    break

        # 输入密码（省略重复代码，保持原逻辑）
        password_selectors = ["input[type='password']", "input[name='password']", "#password", ".password"]
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
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for input_field in inputs:
                if input_field.get_attribute("type") == "password":
                    input_field.send_keys(password)
                    break

        # 勾选同意并登录
        checkbox = driver.find_element(By.CLASS_NAME, "el-checkbox__input")
        checkbox.click()
        denglu_button = driver.find_element(By.CLASS_NAME, "login_btn")
        denglu_button.click()

        time.sleep(3)
        if driver.current_url == "http://10.20.220.251/homePage":
            logger.info("登录成功，等待页面加载...")
            time.sleep(2)

            # 调用其他脚本（如果需要）
            logger.info("登录成功，准备调用test_createmodel.py...")
            current_dir = os.path.dirname(os.path.abspath(__file__))
            move_test_path = os.path.join(current_dir, "test_createmodel.py")
            try:
                subprocess.Popen(["python", move_test_path])
                logger.info("test_createmodel.py已启动")
            except Exception as e:
                logger.error(f"调用test_createmodel.py失败: {str(e)}")

        # 步骤2：执行原 test 函数的逻辑（直接写在这里，作为流程的一部分）
        logger.info("开始执行登录后的操作...")
        a = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='icon_and_text' and span='打开']"))
        )
        a.click()
        time.sleep(2)
        logger.info("点击'打开'按钮成功")

        b=WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='共享空间']"))
        )
        b.click()
        time.sleep(2)
        logger.info("b成功")

        c=WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(By.XPATH,"//span[@class='custom_tree_node']/div/span[text()='模型']")
        )
        c.click()
        time.sleep(2)
        logger.info("c成功")

        d=WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(By.CLASS_NAME,"el-tree-node is-current is-focusable")
        )
        d.find_element_by_xpath(".//span[@class='custom_tree_node']/div/span[text()='模型']").click()

        e


    except Exception as e:
        logger.error(f"流程执行错误: {str(e)}")

# 移除原有的 test 函数（避免被 pytest 识别为独立用例）

# 修复直接运行脚本的入口（如果需要）
if __name__ == '__main__':
    # 手动初始化 driver，不依赖 pytest fixture
    browser_engine = BrowserEngine()
    driver = browser_engine.initialize_driver()

    test_full_flow(driver)  # 调用完整流程函数
