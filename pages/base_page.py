from selenium import webdriver  # 导入Selenium的webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from Log.logger import logger
class BasePase:
    def __init__(self, driver):
        self.driver = driver

    def get_xinjianNum(self):  # 修正方法名（符合PEP8命名规范）
        """获取标签页数量及名称列表"""
        try:
            # # 1. 定位标签页容器（修复多类名定位问题，使用CSS_SELECTOR）
            # tab_container = WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located((
            #         By.CLASS_NAME,  # 多类名用.连接，精准匹配容器
            #         "el-tabs__nav-scroll"
            #     ))
            # )
            # 1. 定位标签页容器（精准匹配包含标签项的父容器）
            tab_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[@class='el-tabs__nav-scroll']/div[@class='el-tabs__nav is-top']"  # 匹配 class 为 el-tabs__nav 和 is-top 的 div
                ))
            )

            # 2. 在容器内定位所有标签项（匹配多类名的标签项）
            tab_items = tab_container.find_elements(
                By.CSS_SELECTOR,
                "div.el-tabs__item.is-top"  # 匹配每个标签项（class 含 el-tabs__item 和 is-top）
            )

            # 3. 提取每个标签的名称
            tab_names = []
            for item in tab_items:
                # 容错处理：防止个别标签缺少名称元素导致整体失败
                try:
                    name_element = item.find_element(
                        By.CLASS_NAME,
                        "scene_name_text"
                    )
                    tab_names.append(name_element.text.strip())

                except Exception as e:
                    print(f"提取单个标签名称失败：{str(e)}")
                    tab_names.append("未知标签")  # 标记异常标签

            logger.info(f"标签长度为: {len(tab_items)}，新建场景为: {tab_names[:]}")

            # 4. 返回结构化结果
            return {
                "count": len(tab_items),
                "names": tab_names
            }

        except Exception as e:
            print(f"获取标签信息失败：{str(e)}")
            return {"count": 0, "names": []}

def set_x_length_by_css_hierarchy(driver):
    try:
        # 2. 逐层定位元素（从外层到内层）
        # 步骤1：定位最外层的 el-form-item 容器
        outer_form = driver.find_element(
            By.CSS_SELECTOR,
            "div.el-form-item.asterisk-left.el-form-item--label-right"
        )

        # 步骤2：在 outer_form 内，定位 el-form-item__content
        form_content = outer_form.find_element(
            By.CSS_SELECTOR,
            "div.el-form-item__content"
        )

        # 步骤3：在 form_content 内，定位 el-input-number
        input_number = form_content.find_element(
            By.CSS_SELECTOR,
            "div.el-input-number"
        )

        # 步骤4：在 input_number 内，定位 el-input
        el_input = input_number.find_element(
            By.CSS_SELECTOR,
            "div.el-input"
        )

        # 步骤5：在 el_input 内，定位目标输入框 el-input__inner
        target_input = el_input.find_element(
            By.CSS_SELECTOR,
            "input.el-input__inner"
        )

        # 3. 修改输入框的值为 2500
        target_input.clear()  # 清空原有值（若需保留可跳过）
        target_input.send_keys("500")  # 输入新值

        # （可选）用 JavaScript 强制设置值（确保值被立即修改）
        # driver.execute_script("arguments[0].value = '2500';", target_input)

        # 验证结果（打印输入框当前值）
        print("输入框当前值：", target_input.get_attribute("value"))

    except Exception as e:
        print(f"定位过程出错：{e}")
    # finally:
    #     driver.quit()  # 无论是否出错，最终关闭浏览器