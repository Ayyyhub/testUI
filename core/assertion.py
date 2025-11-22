from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Log.logger import logger
from core.execute_test_data import UITestExecutor


class customed_assertion:

    def __init__(self, driver):
        self.driver = driver

    """ "元素可见性 / 存在性" """
    def assert_element_visible(self, by,value):
        determine=UITestExecutor(self.driver)
        determine_struct=determine.get_locator(by, value)
        a,b=determine_struct
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((a,b))
            )
            return element.is_displayed()  # 返回布尔值
        except Exception as e:
            # print(f"当前定位方式{determine_struct}")
            # print(f"当前定位方式{a},{b}")
            logger.info(f"断言失败，元素不可见：{str(e)}")
            return False  # 断言失败返回False


    """断言弹窗关闭（元素不可见）"""
    def assert_popup_closed(self, by,value):
        determine = UITestExecutor(self.driver)
        determine_struct = determine.get_locator(by, value)
        a, b = determine_struct
        try:
            # 等待元素不可见
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((a,b))
            )
            return True
        except Exception as e:
            logger.info(f"断言失败,弹窗未关闭：{str(e)}")
            return False



    """断言元素属性状态（启用 / 禁用 / 未选中）"""
    def assert_element_status(driver, xpath, expected_attr, expected_value):

        element = driver.find_element(By.XPATH, xpath)
        actual_value = element.get_attribute(expected_attr)
        assert (
            actual_value == expected_value
        ), f"元素属性 {expected_attr} 预期{expected_value}，实际{actual_value}"

    """断言页面跳转（新页面元素可见）"""
    # def assert_page_jump(driver, new_page_xpath):

    """先输入值，再判断"""
