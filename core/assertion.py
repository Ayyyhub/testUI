from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class customed_assertion:

    def __init__(self,driver):
        self.driver = driver

    """ "元素可见性 / 存在性" """
    # 确保 “预期结果的元素路径（xpath）” 是唯一且稳定的
    def assert_element_visible(self, xpath):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            return element.is_displayed()  # 返回布尔值
        except Exception as e:

            print(f"断言失败：{str(e)}")
            return False  # 断言失败返回False

    """断言弹窗关闭（元素不可见）"""
    def assert_popup_closed(driver, popup_xpath):
        try:
            # 等待元素不可见
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.XPATH, popup_xpath))
            )
        except Exception as e:
            raise AssertionError(f"弹窗未关闭：{str(e)}")


    """断言元素属性状态（启用 / 禁用 / 未选中）"""
    def assert_element_status(driver, xpath, expected_attr, expected_value):

        element = driver.find_element(By.XPATH, xpath)
        actual_value = element.get_attribute(expected_attr)
        assert actual_value == expected_value, f"元素属性 {expected_attr} 预期{expected_value}，实际{actual_value}"


    """断言页面跳转（新页面元素可见）"""
    # def assert_page_jump(driver, new_page_xpath):


    """先输入值，再判断"""