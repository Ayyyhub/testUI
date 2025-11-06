from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Log.logger import logger
import time
import os


def wait_overlays_gone(driver, timeout=10):
    """等待常见遮罩/弹窗消失，避免点击被拦截"""
    overlay_selectors = [
        ".animation_page",
        ".el-message",  # Element UI 消息框
        ".el-loading-mask",  # 加载遮罩
        ".el-dialog__wrapper",  # 弹窗容器
        ".modal-mask",
        "[class*='overlay']",
        "[class*='mask']"
    ]
    for css in overlay_selectors:
        try:
            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, css))
            )
        except Exception:
            # 不可见等待失败也不抛出，交由后续清理逻辑处理
            pass


def wait_element_clickable(driver, locator, timeout=10):
    """等待元素可点击"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        logger.info(f"元素可点击: {locator}")
        return element
    except Exception as e:
        logger.error(f"等待元素可点击失败: {locator}, 错误: {str(e)}")
        return None


def wait_element_visible(driver, locator, timeout=10):
    """等待元素可见"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        logger.info(f"元素可见: {locator}")
        return element
    except Exception as e:
        logger.error(f"等待元素可见失败: {locator}, 错误: {str(e)}")
        return None


def wait_element_invisible(driver, locator, timeout=10):
    """等待元素不可见"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located(locator)
        )
        logger.info(f"元素已不可见: {locator}")
        return True
    except Exception as e:
        logger.warning(f"等待元素不可见失败: {locator}, 错误: {str(e)}")
        return False


def wait_success_messages_gone(driver, timeout=10):
    """等待并关闭可能存在的成功消息弹窗"""
    try:
        success_messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'el-message--success')]")
        if success_messages:
            logger.info("发现成功消息弹窗，等待其消失...")
            # 等待消息自动消失或手动关闭
            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'el-message--success')]"))
            )
            logger.info("成功消息弹窗已消失")
            return True
    except Exception as e:
        logger.warning(f"处理成功消息弹窗时出错: {str(e)}")
    return False


def wait_file_input_available(driver, timeout=10):
    """等待文件输入框可用"""
    file_input = None
    
    # 尝试多种可能的文件输入选择器
    file_input_selectors = [
        "//input[@type='file']"
    ]
    
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
    
    return file_input


def wait_upload_complete(driver, check_function, max_wait_time=300, check_interval=2):
    """等待上传完成"""
    try:
        # 开始等待
        start_time = time.time()
        upload_complete = False
        
        while not upload_complete and (time.time() - start_time) < max_wait_time:
            upload_complete = check_function()
            if upload_complete:
                logger.info(f"上传成功，耗时: {time.time() - start_time:.2f}秒")
                return True
            
            # 每次检查间隔输出一次日志，显示已等待时间
            if int((time.time() - start_time) / 10) * 10 == int(time.time() - start_time):
                logger.info(f"正在等待上传完成，已等待: {time.time() - start_time:.2f}秒")
            
            time.sleep(check_interval)
        
        if not upload_complete:
            logger.warning(f"上传等待超时，已等待{max_wait_time}秒，继续执行后续步骤")
        
        return upload_complete
        
    except Exception as e:
        logger.error(f"等待上传过程中发生错误: {str(e)}")
        return False


def wait_and_click_upload_button(driver, timeout=10):
    """查找并点击可能的上传按钮"""
    try:
        upload_buttons = driver.find_elements(By.XPATH, 
            "//button[contains(text(), '上传') or contains(@class, 'upload')]")
        if upload_buttons:
            upload_buttons[0].click()
            logger.info("点击了可能的上传按钮")
            time.sleep(2)
            return True
    except Exception as e:
        logger.error(f"点击上传按钮失败: {str(e)}")
    return False


def wait_with_retry(driver, action_function, max_retries=3, delay=2):
    """带重试机制的等待"""
    for attempt in range(max_retries):
        try:
            result = action_function()
            if result:
                logger.info(f"操作成功，第{attempt + 1}次尝试")
                return result
        except Exception as e:
            logger.warning(f"第{attempt + 1}次尝试失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    
    logger.error(f"所有{max_retries}次尝试均失败")
    return None