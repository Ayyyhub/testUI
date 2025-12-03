from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Log.logger import logger
import time


"""等待常见遮罩/弹窗消失，避免点击被拦截"""
def wait_overlays_gone(driver, timeout=10):

    overlay_selectors = [
        # ".animation_page",
        ".loader",
        # ".el-message",  # Element UI 消息框
        # ".el-loading-mask",  # 加载遮罩
        # ".el-dialog__wrapper",  # 弹窗容器
        ".el-progress-circle,"
        # ".modal-mask",
        # "[class*='overlay']",
        # "[class*='mask']",
    ]
    for css in overlay_selectors:
        try:
            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, css))
            )
        except Exception:
            # 不可见等待失败也不抛出，交由后续清理逻辑处理
            pass

"""等待元素可点击"""
def wait_element_clickable(driver, locator, timeout=10):

    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        logger.info(f"元素可点击: {locator}")
        return element
    except Exception as e:
        logger.error(f"等待元素可点击失败: {locator}, 错误: {str(e)}")
        return None

"""等待元素可见"""
def wait_element_visible(driver, locator, timeout=10):

    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        logger.info(f"元素可见: {locator}")
        return element
    except Exception as e:
        logger.error(f"等待元素可见失败: {locator}, 错误: {str(e)}")
        return None


"""带重试机制的等待"""
def wait_with_retry(driver, action_function, max_retries=3, delay=2):

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
