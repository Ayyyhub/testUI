from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.excell_reader import Excellreader, AETestData  # 导入你的ExcelReader和TestData
from pages.base_page import BasePase



class UITestExecutor:
    def __init__(self, driver,actions):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)  # 显式等待超时时间
        self.actions = actions
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


    def get_locator(self, determin_method, determin_value):
        """
        解析定位方式+定位值，支持「先父容器后子元素」的分层定位和连续操作
        - 普通定位：返回 (By, 定位值)
        - 分层定位：返回 (父元素WebElement, 子元素By, 子元素定位值)
        - 连续操作：返回 [(By1, 值1), (By2, 值2), ...] 的列表
        """
        # 检查参数是否为空
        if not determin_method or not determin_value:
            raise ValueError(f"定位方式或定位值不能为空: 方式=[{determin_method}], 值=[{determin_value}]")
            
        # 处理连续操作的逻辑（如"xpath,xpath"）
        if "," in determin_method:
            # 拆分多个定位方式
            methods = determin_method.split(",")
            
            # 检查定位值是否也有对应数量的分隔
            if "||" not in determin_value or determin_value.count("||") != len(methods) - 1:
                raise ValueError(f"连续操作时，定位值必须用'||'分隔，且数量与定位方式匹配: 方式=[{determin_method}], 值=[{determin_value}]")
            
            # 拆分多个定位值
            values = determin_value.split("||")
            
            # 构建连续操作的定位器列表
            locators = []
            for i, method in enumerate(methods):
                method = method.strip()  # 去除可能的空格
                by = self.locator_map.get(method.lower())
                if not by:
                    raise ValueError(f"不支持的定位方式: [{method}]，支持的定位方式有: {list(self.locator_map.keys())}")
                locators.append((by, values[i].strip()))
            
            # 返回连续操作的定位器列表，添加特殊标记表示这是连续操作
            return {"type": "sequential", "locators": locators}
            
        # 处理「先定位父容器」的逻辑
        elif determin_method == "xpath(先定位父容器)":
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
                raise ValueError(f"不支持的定位方式: [{determin_method}]，支持的定位方式有: {list(self.locator_map.keys())}")
            return (by, determin_value)

    def execute_step(self, step):
        """根据测试步骤执行UI操作（兼容分层定位和连续操作）"""
        try:
            print(f"执行步骤 {step.step_id}: {step.description}")
            print(f"操作类型：[{step.determin_type}], 定位方式: [{step.determin_method}], 定位值: [{step.determin_value}]")
            element = None
            by = None
            value = None

            # 1. 获取定位器（支持分层/普通/连续三种格式）
            try:
                locator = self.get_locator(step.determin_method, step.determin_value)
            except Exception as e:
                print(f"❌ 获取定位器失败: {str(e)}")
                step.outputed_result = f"获取定位器失败: {str(e)}"
                step.status = "FAIL"
                return

            # 2. 解析定位器，找到目标元素
            # 处理连续操作的情况
            if isinstance(locator, dict) and locator.get("type") == "sequential":
                # 连续操作的情况

                # 执行每一步定位和点击
                for i, loc in enumerate(locator['locators']):
                    by, value = loc
                    print(f"执行第{i+1}步定位: 方式——[{by}], 值——[{value}]")

                    # 等待元素可点击并点击
                    element = self.wait.until(
                        EC.presence_of_element_located((by, value))
                    )

                    # 除了最后一个元素外，其他都执行点击
                    if i < len(locator['locators']) - 1:
                        # 点击前等待遮罩消失
                        self.wait_overlays_gone(timeout=10)
                        clickable_elem = self.wait.until(EC.element_to_be_clickable((by, value)))
                        try:
                            # 先滚动到视图中间
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});",
                                                       clickable_elem)
                            clickable_elem.click()
                            print(f"第{i + 1}步点击成功")
                        except Exception as e:
                            if "element click intercepted" in str(e).lower():
                                print("第{}步点击被拦截，清理遮罩后重试...".format(i + 1))

                                self.wait_overlays_gone(timeout=10)
                                try:
                                    clickable_elem = self.wait.until(EC.element_to_be_clickable((by, value)))
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});",
                                                               clickable_elem)
                                    clickable_elem.click()
                                    print(f"第{i + 1}步点击成功（重试）")
                                except Exception:
                                    # 最后兜底：JS点击
                                    self.driver.execute_script("arguments[0].click();", element)
                                    print(f"第{i + 1}步通过JavaScript点击成功")
                            else:
                                raise e

                    # 最后一个元素不自动点击，留给后续操作处理
                    print(f"连续操作定位完成，最后一个元素已找到")

            elif isinstance(locator, tuple):
                if len(locator) == 3:
                    # 分层定位：父元素内找子元素
                    parent_elem, child_by, child_value = locator
                    element = parent_elem.find_element(child_by, child_value)
                    by, value = child_by, child_value
                    print(f"分层定位成功：父容器内找到子元素，定位方式[{child_by}]，值[{child_value}]")
                else:
                    # 普通定位：直接找元素
                    by, value = locator
                    element = self.wait.until(
                        EC.presence_of_element_located((by, value))
                    )
                    print(f"普通定位成功：定位方式——[{by}]，值——[{value}]")
            else:
                raise ValueError("定位器格式错误，需为元组或字典")

            # 3. 根据操作类型执行动作（click/input/verify等）
            action = step.determin_type  # 假设Excel中"操作类型"字段存click/input等

            if action == "click":
                clickable_elem = self.wait.until(
                    EC.element_to_be_clickable(element if element else (by, value))
                )
                try:
                    clickable_elem.click()
                    step.outputed_result = "点击成功"
                    step.status = "PASS"
                except Exception as e:
                    if "element click intercepted" in str(e).lower():
                        print("常规点击被拦截，清理遮罩后重试...")

                        self.wait_overlays_gone(timeout=10)
                        try:
                            clickable_elem = self.wait.until(
                                EC.element_to_be_clickable(element if element else (by, value))
                            )
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});",
                                                       clickable_elem)
                            clickable_elem.click()
                            step.outputed_result = "点击成功（重试）"
                            step.status = "PASS"
                        except Exception:
                            print("重试仍失败，使用JavaScript点击兜底")
                            self.driver.execute_script("arguments[0].click();", element)
                            step.outputed_result = "通过JavaScript点击成功"
                            step.status = "PASS"
                    else:
                        raise e

            elif action == "input":
                element.clear()
                element.send_keys(step.input_value)
                step.outputed_result = f"输入内容: {step.input_value}"
                step.status = "PASS"

            elif action == "context_click":
                action1=ActionChains(self.actions)
                context_clickable_elem = self.wait.until(
                    EC.element_to_be_clickable(element if element else (by, value))
                )
                try:
                    action1.context_click(context_clickable_elem).perform()
                    step.outputed_result = "点击成功"
                    step.status = "PASS"
                except Exception as e:
                    if "element click intercepted" in str(e).lower():
                        # 尝试使用JavaScript点击
                        print(f"常规点击被拦截，尝试使用JavaScript点击")
                        self.driver.execute_script("arguments[0].click();", element)
                        step.outputed_result = "通过JavaScript点击成功"
                        step.status = "PASS"
                    else:
                        raise e



            ### 验证
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

    def wait_overlays_gone(self, timeout=10):
        """等待常见遮罩/弹窗消失，避免点击被拦截"""
        overlay_selectors = [
            ".animation_page",
            ".el-message",                  # Element UI 消息框
            ".el-loading-mask",             # 加载遮罩
            ".el-dialog__wrapper",          # 弹窗容器
            ".modal-mask",
            "[class*='overlay']",
            "[class*='mask']"
        ]
        for css in overlay_selectors:
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, css))
                )
            except Exception:
                # 不可见等待失败也不抛出，交由后续清理逻辑处理
                pass

