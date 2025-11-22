import pytest
from Log.logger import logger
from pages.base_page import BasePase
from utils.wait_clickable import wait_overlays_gone
import time
from selenium.webdriver.common.by import By


class NewcreateHelper:

    # @pytest.mark.dependency(depends=["login"],name="newcreate")
    # @pytest.mark.run(order=2)
    def newcreate_func(self, driver):
        logger.info("=== 开始执行点击新建场景 ===")
        self.driver = driver  # 保存driver到实例，后续用self.driver,如果后续有其他方法在同一个类下，无需再传 driver 参数

        try:
            logger.info("点击新建场景")

            wait_overlays_gone(self.driver, timeout=10)

            new_clik = driver.find_element(
                By.XPATH,
                '//div[@class="icon_and_text" and span[text()="新建"]]',
            )
            new_clik.click()
            time.sleep(3)
            # 断言
            basepage = BasePase(driver=self.driver)
            tab_info = basepage.get_xinjianNum()

            if tab_info["count"] >= 1:
                logger.info("与预期结果一致,断言新建场景成功")

        except Exception as e:
            print(e)
