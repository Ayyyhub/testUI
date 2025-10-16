# from telnetlib import EC
from selenium.webdriver.support import expected_conditions as EC
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from pages.base_page import BasePase
from core.logger import logger
import time
import os
from utils.wait_clickable import wait_overlays_gone
from testcases.test_login import Test_login


class aTest_upload:
    # @pytest.mark.dependency(name="upload")
    # @pytest.mark.run(order=2)
    def atest_upload(self, driver):
        self.driver = driver
        upload_success = False  # 添加上传成功标志

        # test_login_shili = Test_login()
        # test_login_shili.test_login_func(driver)

        try:
            logger.info("点击新建场景")

            wait_overlays_gone(self.driver, timeout=10)

            new_clik = driver.find_element(By.XPATH, '//div[@class="icon_and_text" and span[text()="新建"]]')
            new_clik.click()
            time.sleep(3)
            # 断言
            basepage = BasePase(driver=self.driver)
            tab_info = basepage.get_xinjianNum()

            if tab_info['count'] >= 1:
                print("与预期结果一致,断言新建场景成功")
                try:
                    logger.info("##### 开始上传模型 #####")
                    time.sleep(2)
                    
                    # 等待并关闭可能存在的成功消息弹窗
                    try:
                        success_messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'el-message--success')]")
                        if success_messages:
                            logger.info("发现成功消息弹窗，等待其消失...")
                            # 等待消息自动消失或手动关闭
                            WebDriverWait(driver, 10).until(
                                EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'el-message--success')]"))
                            )
                            logger.info("成功消息弹窗已消失")
                    except Exception as e:
                        logger.warning(f"处理成功消息弹窗时出错: {str(e)}")
                    
                    wait = WebDriverWait(driver, 10)
                    
                    # 点击上传按钮
                    element = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, '//li[contains(@class,"el-menu-item")][5]/div//span[text()="上传"]')))
                    element.click()
                    
                    # ========== 浏览器内文件上传处理 ==========
                    # 1. 查找隐藏的文件输入框
                    try:
                        # 等待文件输入框出现（可能是隐藏的）
                        time.sleep(2)
                        
                        # 尝试多种可能的文件输入选择器
                        file_input_selectors = [
                            "//input[@type='file']"
                        ]
                        
                        file_input = None
                        for selector in file_input_selectors:
                            try:
                                # 尝试找到文件输入元素
                                elements = driver.find_elements(By.XPATH, selector)
                                if elements:
                                    file_input = elements[0]
                                    logger.info(f"找到文件输入框: {selector}")
                                    break
                            except Exception as e:
                                logger.warning(f"尝试选择器 {selector} 失败: {str(e)}")
                        
                        if not file_input:
                            # 如果没有找到，尝试使用JavaScript查找所有input[type=file]
                            logger.info("通过XPath未找到文件输入框，尝试使用JavaScript...")
                            file_inputs = driver.execute_script("""
                                return Array.from(document.querySelectorAll('input[type="file"]'));
                            """)
                            
                            if file_inputs:
                                file_input = file_inputs[0]
                                logger.info("通过JavaScript找到文件输入框")

                        ###  上传文件
                        if file_input:
                            # 设置文件路径
                            file_path = os.path.abspath(r"D:\AE_myspace\Ae_机器人场景\BXMD74.step")
                            logger.info(f"准备上传文件: {file_path}")
                            
                            # 使用JavaScript使元素可见（如果它是隐藏的）
                            driver.execute_script("arguments[0].style.display = 'block';", file_input)
                            
                            # 发送文件路径到输入框
                            file_input.send_keys(file_path)
                            logger.info("已发送文件路径到输入框")
                            
                            # 等待上传完成 - 使用显式等待替代固定时间等待
                            try:
                                # 最长等待时间（秒）
                                max_wait_time = 300  # 5分钟
                                # 检查间隔（秒）
                                check_interval = 2
                                
                                # 定义上传完成的检查函数
                                def is_upload_complete():
                                    try:
                                            
                                        # 方法3：检查是否出现了上传后的元素（如模型预览或模型名称）
                                        model_elements = driver.find_elements(By.XPATH, 
                                            "//div[contains(@class,'label_content')]/span[contains(text(),'BXMD74_15')]")
                                        if model_elements:
                                            return True
                                            
                                        return False
                                    except Exception as e:
                                        logger.error(f"检查上传状态时出错: {str(e)}")
                                        return False
                                
                                # 开始等待
                                start_time = time.time()
                                upload_complete = False
                                
                                while not upload_complete and (time.time() - start_time) < max_wait_time:
                                    upload_complete = is_upload_complete()
                                    if upload_complete:
                                        logger.info(f"文件上传成功，耗时: {time.time() - start_time:.2f}秒")
                                        upload_success=True
                                        break
                                    
                                    # 每次检查间隔输出一次日志，显示已等待时间
                                    if int((time.time() - start_time) / 10) * 10 == int(time.time() - start_time):
                                        logger.info(f"正在等待上传完成，已等待: {time.time() - start_time:.2f}秒")
                                    
                                    time.sleep(check_interval)
                                
                                if not upload_complete:
                                    logger.warning(f"上传等待超时，已等待{max_wait_time}秒，继续执行后续步骤")
                                
                            except Exception as e:
                                logger.error(f"等待上传过程中发生错误: {str(e)}")

                        else:
                            logger.error("无法找到文件输入框")
                            
                            # 尝试查找并点击可能的上传按钮，然后再次检查
                            upload_buttons = driver.find_elements(By.XPATH, 
                                "//button[contains(text(), '上传') or contains(@class, 'upload')]")
                            if upload_buttons:
                                upload_buttons[0].click()
                                logger.info("点击了可能的上传按钮，重新检查文件输入框")
                                time.sleep(2)
                                
                                # 再次尝试查找文件输入框
                                file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                                if file_inputs:
                                    file_input = file_inputs[0]
                                    file_path = os.path.abspath(r"D:\AE_myspace\Ae_机器人场景\BXMD74.step")
                                    driver.execute_script("arguments[0].style.display = 'block';", file_input)
                                    file_input.send_keys(file_path)
                                    logger.info("第二次尝试：已发送文件路径到输入框")
                                    time.sleep(5)
                                else:
                                    logger.error("第二次尝试仍无法找到文件输入框")
                    
                    except Exception as e:
                        logger.error(f"处理文件上传失败: {str(e)}")
                        # 记录页面源代码，帮助调试
                        page_source = driver.page_source
                        logger.info(f"页面源代码片段: {page_source[:500]}...")  # 只记录前500个字符
                
                except Exception as e:
                    logger.error(f"上传模型失败：{str(e)}")
                    upload_success = False
        
        except Exception as e:
            logger.error(e)
            upload_success = False
            
        # 根据实际上传结果返回
        if upload_success:
            logger.info("上传流程完成且验证成功")
            return True
        else:
            logger.error("上传流程失败或验证失败")
            return False

