from pywinauto import Application
from selenium.webdriver.common.by import By

from pages.base_page import BasePase
from utils.conf_reader import load_config
from core.logger import logger
import time

class Test_upload:

    def test_upload(self,driver):
        self.driver = driver
        try:
            logger.info("点击新建场景")

            # driver.find_element(By.XPATH,'//div[@class="icon_and_text' and span="新建"]')
            new_clik=driver.find_element(By.XPATH, '//div[@class="icon_and_text" and span[text()="新建"]]')
            new_clik.click()
            #断言
            basepage = BasePase(driver=self.driver)
            tab_info = basepage.get_xinjianNum()
            if tab_info['count'] == 2:
                print("与预期结果一致,断言成功")
        except Exception as e:
            logger.error(e)
        try:
            logger.info("开始上传模型")

            ele_clik=driver.find_element(By.XPATH,'//li[@class="el-menu-item is-active"]')
            ele_clik.click()

            # 等待系统文件选择对话框弹出（根据实际情况调整等待时间）
            time.sleep(2)

            # ========== 2. Pywinauto 操作：控制 Windows 文件选择对话框 ==========
            # 连接到“打开”对话框（标题匹配“打开”，超时 10 秒）
            app = Application(backend="uia").connect(title_re="打开", timeout=10)
            file_dialog = app.window(title_re="打开")  # 获取对话框对象

            # 定位“文件名”输入框，填入要上传的文件路径
            file_path = r"D:\AE_myspace\Ae_机器人场景\BXMD74.step"
            file_dialog["文件名:Edit"].set_text(file_path)

            # 点击“打开”按钮，完成文件上传
            file_dialog["打开(O)"].click()


            assert_file = driver.find_element()
            logger.info(f"成功触发上传：{file_path}")
        except Exception as e:
            logger.error(f"上传模型失败：{str(e)}")
            raise

