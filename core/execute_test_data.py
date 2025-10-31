import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.excell_reader import Excellreader, AETestData  # 导入你的ExcelReader和TestData
from pages.base_page import BasePase
from utils.perfomance.performance_decorator import monitored_performancer
from utils.wait_clickable import wait_overlays_gone


class UITestExecutor:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)  # 显式等待超时时间
        # self.actions = actions
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


    def get_locator(self, determin_method, determin_value):
        """
        解析定位方式+定位值，支持「先父容器后子元素」的分层定位和连续操作
        - 单次定位：返回 (By, 定位值)
        - 分层定位：返回 (父元素WebElement, 子元素By, 子元素定位值)
        - 连续操作：返回 [(By1, 值1), (By2, 值2), ...] 的列表
        """
        # 检查参数是否为空
        if not determin_method or not determin_value:
            raise ValueError(f"定位方式或定位值不能为空: 方式=[{determin_method}], 值=[{determin_value}]")
            
        # 1、处理连续操作的逻辑（如"xpath,xpath"）
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
            
        # 2、处理「先定位父容器」的逻辑
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

        # 3、处理单个元素定位
        else:
            # 处理普通定位（id、css等）
            by = self.locator_map.get(determin_method.lower())
            if not by:
                raise ValueError(f"不支持的定位方式: [{determin_method}]，支持的定位方式有: {list(self.locator_map.keys())}")

            return (by, determin_value)


    # @monitored_performancer("execute_step")
    def execute_step(self, step):
        """根据测试步骤执行UI操作（兼容分层定位和连续操作）"""
        try:
            print(f"执行步骤 {step.step_id}: {step.description}")
            if step.determin_type=="input":
                print(f"操作类型：[{step.determin_type}], 定位方式: [{step.determin_method}], 定位值: [{step.determin_value}], 输入值：[{step.input_value}]")
            else:
                print(f"操作类型：[{step.determin_type}], 定位方式: [{step.determin_method}], 定位值: [{step.determin_value}]")
            element = None
            by = None
            value = None

            # 1. 获取定位器（支持分层/普通/连续三种格式）
            try:
                locator_dict = self.get_locator(step.determin_method, step.determin_value)
            except Exception as e:
                print(f"❌ 获取定位器失败: {str(e)}")
                step.outputed_result = f"获取定位器失败: {str(e)}"
                step.status = "FAIL"
                return

            # 2. 解析定位器，找到目标元素
            # 2.1 处理连续操作的情况,isinstance 是 Python 的内置函数,用于判断一个对象是否属于某个指定的类型,locator_dict 是一个字典，包含 type 和 locators列表
            if isinstance(locator_dict, dict) and locator_dict.get("type") == "sequential":
                # 连续操作的情况
                if step.determin_type == "click":
                    # 执行每一步定位和点击
                    for i, loc in enumerate(locator_dict['locators']):
                        by, value = loc
                        print(f"执行第{i+1}步定位: 方式：[{by}], 值：[{value}]")

                        # 当有多个元素时，除了最后一个元素外，其他都执行点击
                        if i < len(locator_dict['locators']) - 1:

                            # 点击前等待遮罩消失
                            wait_overlays_gone(self.driver,timeout=10)

                            # presence_of_element_located	只检查元素在DOM中存在	需要获取元素属性、文本内容等
                            # element_to_be_clickable	检查存在+可见+可点击	需要进行点击操作时
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

                                    wait_overlays_gone(self.driver,timeout=10)
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

                elif step.determin_type == "drag_and_drop":
                    try:
                        print(
                            f"执行第1步定位：方式：“{locator_dict['locators'][0][0]}”，值:“{locator_dict['locators'][0][1]}”")
                        drag_elem = self.wait.until(
                            EC.presence_of_element_located((
                                locator_dict["locators"][0][0],
                                locator_dict["locators"][0][1]
                            ))
                        )
                        print(
                            f"执行第2步定位：方式：“{locator_dict['locators'][1][0]}”，值:“{locator_dict['locators'][1][1]}”")
                        drop_elem = self.wait.until(
                            EC.presence_of_element_located((
                                locator_dict["locators"][1][0],
                                locator_dict["locators"][1][1]
                            ))
                        )
                        
                        # 确保元素可见和可交互
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", drag_elem)
                        time.sleep(1)  # 等待滚动完成
                        
                        # 执行拖拽
                        action_drag = ActionChains(self.driver)
                        action_drag.drag_and_drop(drop_elem, drag_elem).perform()
                        time.sleep(1)  # 等待拖拽动画完成
                        step.outputed_result = "拖拽操作成功"
                        step.status = "PASS"
                        print(step.status)
                    except Exception as e:
                        print(f"拖拽操作失败: {str(e)}")
                        step.outputed_result = f"拖拽操作失败: {str(e)}"
                        step.status = "FAIL"
                else:
                    raise ValueError(f"连续操作不支持的操作类型: [{step.determin_type}]，支持的操作类型有: click, drag_and_drop")
            
            # 2.2 单个操作，locator_dict 是元组，包含定位方式和值
            elif isinstance(locator_dict, tuple):
                # 有3个定位值时，待完善!
                if len(locator_dict) == 3:
                    # 分层定位：父元素内找子元素
                    parent_elem, child_by, child_value = locator_dict
                    element = parent_elem.find_element(child_by, child_value)
                    by, value = child_by, child_value
                    print(f"分层定位成功：父容器内找到子元素，定位方式：[{child_by}]，值：[{child_value}]")

                else:
                    # ============普通定位，直接找元素，只有1个定位值！============
                    by, value = locator_dict
                    element = self.wait.until(
                        # presence_of_element_located是Expected Condition之一,表示检查页面上是否存在指定的元素,
                        # 只要元素出现在DOM中就会返回，即使它不可见
                        EC.presence_of_element_located((by, value))
                        #EC.element_to_be_clickable((by, value))
                    )
                    if step.determin_method=="input":
                        print(f"普通定位成功，定位方式：[{by}]，定位值：[{value}],输入数据：[{step.input_value}]")
                    else:
                        print(f"普通定位成功，定位方式：[{by}]，值：[{value}]")
            else:
                raise ValueError("定位器格式错误，需为元组或字典")

            # ============ 执行点击 ============
            # 3. 根据操作类型执行动作（click/input/verify等）
            action = step.determin_type  # 假设Excel中"操作类型"字段存click/input等
            if action == "click":
                # element 已经是定位到的元素了，不需要再用 element if element else (by, value) 判断。
                clickable_elem = self.wait.until(
                    EC.presence_of_element_located((by, value))
                )
                try:
                    time.sleep(1)
                    clickable_elem.click()
                    time.sleep(2)
                    step.outputed_result = "点击成功"
                    step.status = "PASS"
                    print(step.status)
                except Exception as e:
                    if "element click intercepted" in str(e).lower():
                        print("常规点击被拦截，清理遮罩后重试...")

                        wait_overlays_gone(self.driver,timeout=10)
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

                # new_value = step.input_value  # 要设置的新值
                # self.driver.execute_script(f"arguments[0].value = '{new_value}';", element)

                time.sleep(1)
                step.outputed_result = f"输入内容: {step.input_value}"
                step.status = "PASS"

            elif action == "context_click":
                action_context = ActionChains(self.driver)
                context_clickable_elem = self.wait.until(
                    EC.element_to_be_clickable(element if element else (by, value))
                )
                try:
                    action_context.context_click(context_clickable_elem).perform()
                    time.sleep(2)
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

            elif action == "double_click":
                action_double = ActionChains(self.driver)
                action_double_elem = self.wait.until(
                    EC.element_to_be_clickable(element if element else (by, value))
                )
                try:
                    action_double.double_click(action_double_elem).perform()
                    time.sleep(2)
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



