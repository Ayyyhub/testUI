from selenium import webdriver  # 导入Selenium的webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from core.logger import logger
class BasePase:
    def __init__(self, driver):
        self.driver = driver

    def get_xinjianNum(self):  # 修正方法名（符合PEP8命名规范）
        """获取标签页数量及名称列表"""
        try:
            # 1. 定位标签页容器（修复多类名定位问题，使用CSS_SELECTOR）
            tab_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.CLASS_NAME,  # 多类名用.连接，精准匹配容器
                    "el-tabs__nav-scroll"
                ))
            )
            logger.info(f"tab_container:{tab_container.text}")

            # 2. 在容器内定位所有标签项（使用CSS_SELECTOR确保稳定性）
            tab_items = tab_container.find_elements(
                By.CSS_SELECTOR,
                "div.el-tabs__item.is-top"  # 所有标签项的共同类名组合
            )
            logger.info(f"tab_items:{len(tab_items)}")
            print(f"所有标签：{tab_items}")

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

            # 4. 返回结构化结果
            return {
                "count": len(tab_items),
                "names": tab_names
            }

        except Exception as e:
            print(f"获取标签信息失败：{str(e)}")
            return {"count": 0, "names": []}

