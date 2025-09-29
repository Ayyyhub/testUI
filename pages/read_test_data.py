import logging

from core.logger import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.excell_reader import Excellreader, TestData  # 导入你的ExcelReader和TestData
from pages.base_page import BasePase



class UITestExecutor:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)  # 显式等待超时时间

        # 定位方式映射：将Excel中的"定位方式"字符串转换为Selenium的By对象
        self.locator_map = {
            "id": By.ID,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css": By.CSS_SELECTOR,
            "class": By.CLASS_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link": By.PARTIAL_LINK_TEXT
        }
        # basepage = BasePase(driver)


    def get_locator(self, determin_method: str, determin_value: str):
        """将Excel中的定位方式和定位值转换为Selenium的定位器"""
        by = self.locator_map.get(determin_method.lower())
        if not by:
            raise ValueError(f"不支持的定位方式: {determin_method}")
        return (by, determin_value)

    def execute_step(self, step: TestData):
        """根据测试步骤数据执行具体UI操作"""
        try:
            print(f"执行步骤 {step.step_id}: {step.description}")

            # 获取定位器
            locator = self.get_locator(step.determin_method, step.determin_value)

            # 根据操作类型执行对应动作（这里需要根据你的Excel中"操作类型"的定义来扩展）
            # 假设Excel中有一列表示操作类型（如"click"、"input"、"select"等）
            # 这里以常见操作为例，你需要根据实际的Excel字段名调整
            action = step.determin_type  # 假设"determin_type"实际存储的是操作类型

            if action == "click":
                # 点击操作
                element = self.wait.until(EC.element_to_be_clickable(locator))
                element.click()
                print("点击成功")

                # #断言
                # basepage=BasePase(driver=self.driver)
                # tab_info =basepage.get_xinjianNum()
                #
                # if tab_info['count']==step.expected_result:
                #     print("与预期结果一致")
                #     logger.info("与预期结果一致")
                #     step.status="PASS"
                # else:
                #     step.status="FAIL"

            elif action == "input":
                # 输入操作
                element = self.wait.until(EC.visibility_of_element_located(locator))
                element.clear()
                element.send_keys(step.input_value)
                step.outputed_result = f"输入内容: {step.input_value}"
                step.status = "PASS"

            elif action == "verify":
                # 验证操作（检查预期结果）
                element = self.wait.until(EC.visibility_of_element_located(locator))
                actual_text = element.text
                if actual_text == step.expected_result:
                    step.outputed_result = f"验证成功，实际值: {actual_text}"
                    step.status = "PASS"
                else:
                    step.outputed_result = f"验证失败，预期: {step.expected_result}, 实际: {actual_text}"
                    step.status = "FAIL"

            else:
                step.outputed_result = f"不支持的操作类型: {action}"
                step.status = "ERROR"

        except Exception as e:
            step.outputed_result = f"操作失败: {str(e)}"
            step.status = "FAIL"
            print(f"步骤 {step.step_id} 执行失败: {str(e)}")



