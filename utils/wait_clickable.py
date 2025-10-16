from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


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