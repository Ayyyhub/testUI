import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 导入init.py中的初始化函数
from core.browser_engine import BrowserEngine
from core.logger import logger  # 导入封装好的 logger
from pages.base_page import set_x_length_by_css_hierarchy

class Test_createmodel:


    # @pytest.mark.dependency(depends=["newcreate"],name="createmodel")
    @pytest.mark.run(order=3)
    def test_createmodel_func(self,driver):
        self.driver = driver  # 保存driver到实例，后续用self.driver,如果后续有其他方法在同一个类下，无需再传 driver 参数
        try:
            logger.info("开始创建模型测试...")

            model=driver.find_element(By.XPATH,'//div[@class="collapse_item_title"]//span[text()="模型"]')
            model.click()

            # 使用当前浏览器实例查找创建模型按钮
            # 等待创建模型按钮出现
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="child_btns" and .//span="创建模型"]'))
            )
            create_model = driver.find_element(By.XPATH, '//div[@class="child_btns" and .//span="创建模型"]')
            print("找到创建模型按钮，点击...")
            create_model.click()

            #设置x长度
            set_x_length_by_css_hierarchy(driver)

            # 1. 先定位父容器
            parent_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.space-around.flex.margin"))
            )
            # # 2. 在父容器内定位“确定”按钮（注意XPath前加"."表示在当前元素内查找）
            # confirm_btn_in_parent = parent_div.find_element(By.XPATH, ".//button[text()='确定']")
            # confirm_btn_in_parent.click()
            # 再等父容器内的按钮可点击
            confirm_btn_in_parent = WebDriverWait(parent_div, 10).until(
                EC.element_to_be_clickable((By.XPATH, ".//button[.//span[text()='确定']]"))  # 修正XPath
            )
            confirm_btn_in_parent.click()
            time.sleep(3)
            # 尝试打印当前页面URL和标题，帮助调试
            print("当前页面URL:", driver.current_url)
            print("当前页面标题:", driver.title)


        except Exception as e:
            logger.error(f"创建模型测试失败: {e}")
            return False
