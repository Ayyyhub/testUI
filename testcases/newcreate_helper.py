import pytest
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
                By.XPATH, '//div[@class="icon_and_text" and span[text()="新建"]]')
            new_clik.click()
            time.sleep(3)
            # 断言
            basepage = BasePase(driver=self.driver)
            tab_info = basepage.get_xinjianNum()

            if tab_info['count'] >= 1:
                logger.info("与预期结果一致,断言新建场景成功")
                # try:
                #     logger.info("##### 开始上传模型 #####")
                #     time.sleep(2)
                #
                #     # 等待并关闭可能存在的成功消息弹窗
                #     try:
                #         success_messages = driver.find_elements(By.XPATH,
                #                                                 "//div[contains(@class, 'el-message--success')]")
                #         if success_messages:
                #             logger.info("发现成功消息弹窗，等待其消失...")
                #             # 等待消息自动消失或手动关闭
                #             WebDriverWait(driver, 10).until(
                #                 EC.invisibility_of_element_located(
                #                     (By.XPATH, "//div[contains(@class, 'el-message--success')]"))
                #             )
                #             logger.info("成功消息弹窗已消失")
                #     except Exception as e:
                #         logger.warning(f"处理成功消息弹窗时出错: {str(e)}")
                #
                #     wait = WebDriverWait(driver, 10)
                #
                #     # 点击上传按钮
                #     element = wait.until(EC.element_to_be_clickable(
                #         (By.XPATH, '//li[contains(@class,"el-menu-item")][5]/div//span[text()="上传"]')))
                #     element.click()
                # except Exception as e:
                #     print(e)
        except Exception as e:
            print(e)
