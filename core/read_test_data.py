import logging

from core.logger import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.excell_reader import Excellreader, AETestData  # 导入你的ExcelReader和TestData
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


    # def get_locator(self, determin_method: str, determin_value: str):
    #     """将Excel中的定位方式和定位值转换为Selenium的定位器"""
    #     by = self.locator_map.get(determin_method.lower())
    #     if not by:
    #         raise ValueError(f"不支持的定位方式: {determin_method}")
    #     return (by, determin_value)
    #
    # def execute_step(self, step: TestData):
    #     """根据测试步骤数据执行具体UI操作"""
    #     try:
    #         print(f"执行步骤 {step.step_id}: {step.description}")
    #
    #         # 获取定位器
    #         locator = self.get_locator(step.determin_method, step.determin_value)
    #
    #         # 根据操作类型执行对应动作（这里需要根据你的Excel中"操作类型"的定义来扩展）
    #         # 假设Excel中有一列表示操作类型（如"click"、"input"、"select"等）
    #         # 这里以常见操作为例，你需要根据实际的Excel字段名调整
    #         action = step.determin_type  # 假设"determin_type"实际存储的是操作类型
    #
    #         if action == "click":
    #             # 点击操作
    #             element = self.wait.until(EC.element_to_be_clickable(locator))
    #             element.click()
    #             print("点击成功")
    #
    #             # #断言
    #             # basepage=BasePase(driver=self.driver)
    #             # tab_info =basepage.get_xinjianNum()
    #             #
    #             # if tab_info['count']==step.expected_result:
    #             #     print("与预期结果一致")
    #             #     logger.info("与预期结果一致")
    #             #     step.status="PASS"
    #             # else:
    #             #     step.status="FAIL"
    #
    #         elif action == "input":
    #             # 输入操作
    #             element = self.wait.until(EC.visibility_of_element_located(locator))
    #             element.clear()
    #             element.send_keys(step.input_value)
    #             step.outputed_result = f"输入内容: {step.input_value}"
    #             step.status = "PASS"
    #
    #         elif action == "verify":
    #             # 验证操作（检查预期结果）
    #             element = self.wait.until(EC.visibility_of_element_located(locator))
    #             actual_text = element.text
    #             if actual_text == step.expected_result:
    #                 step.outputed_result = f"验证成功，实际值: {actual_text}"
    #                 step.status = "PASS"
    #             else:
    #                 step.outputed_result = f"验证失败，预期: {step.expected_result}, 实际: {actual_text}"
    #                 step.status = "FAIL"
    #
    #         else:
    #             step.outputed_result = f"不支持的操作类型: {action}"
    #             step.status = "ERROR"
    #
    #     except Exception as e:
    #         step.outputed_result = f"操作失败: {str(e)}"
    #         step.status = "FAIL"
    #         print(f"步骤 {step.step_id} 执行失败: {str(e)}")

    def get_locator(self, determin_method, determin_value):
        """
        解析定位方式+定位值，支持「先父容器后子元素」的分层定位
        - 普通定位：返回 (By, 定位值)
        - 分层定位：返回 (父元素WebElement, 子元素By, 子元素定位值)
        """
        # 处理「先定位父容器」的逻辑（示例：定位方式为"xpath(先定位父容器)"）
        if determin_method == "xpath(先定位父容器)":
            if "||" in determin_value:
                # 拆分父容器定位和子元素定位（用||分隔）
                parent_locator, child_locator = determin_value.split("||", 1)
                # 先等待父容器出现
                parent_elem = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, parent_locator))
                )
                return (parent_elem, By.XPATH, child_locator)
            else:
                # 无分隔符时，直接用XPath定位子元素
                return (By.XPATH, determin_value)
        else:
            # 处理普通定位（id、css等）
            by = self.locator_map.get(determin_method.lower())
            if not by:
                raise ValueError(f"不支持的定位方式: {determin_method}")
            return (by, determin_value)

    def execute_step(self, step):
        """根据测试步骤执行UI操作（兼容分层定位）"""
        try:
            print(f"执行步骤 {step.step_id}: {step.description}")
            element = None

            # 1. 获取定位器（支持分层/普通两种格式）
            locator = self.get_locator(step.determin_method, step.determin_value)

            # 2. 解析定位器，找到目标元素
            if isinstance(locator, tuple):
                if len(locator) == 3:
                    # 分层定位：父元素内找子元素
                    parent_elem, child_by, child_value = locator
                    element = parent_elem.find_element(child_by, child_value)
                    print(f"✅ 分层定位成功：父容器内找到子元素，定位方式[{child_by}]，值[{child_value}]")
                else:
                    # 普通定位：直接找元素
                    by, value = locator
                    element = self.wait.until(
                        EC.presence_of_element_located((by, value))
                    )
                    print(f"✅ 普通定位成功：定位方式[{by}]，值[{value}]")
            else:
                raise ValueError("定位器格式错误，需为元组")

            # 3. 根据操作类型执行动作（click/input/verify等）
            action = step.determin_type  # 假设Excel中“操作类型”字段存click/input等

            if action == "click":
                clickable_elem = self.wait.until(
                    EC.element_to_be_clickable(element if element else (by, value))
                )
                clickable_elem.click()
                step.outputed_result = "点击成功"
                step.status = "PASS"

            elif action == "input":
                element.clear()
                element.send_keys(step.input_value)
                step.outputed_result = f"输入内容: {step.input_value}"
                step.status = "PASS"

            elif action == "verify":
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
            print(f"❌ 步骤 {step.step_id} 执行失败: {str(e)}")

