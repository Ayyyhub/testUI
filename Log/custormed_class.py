# 自定义异常体系类

# 测试用例层 (test_*.py)
#     ↓ 捕获业务异常
# 业务流程层 (LoginPage, OrderPage)
#     ↓ 捕获操作异常
# 页面操作层 (BasePage - click, input等)
#     ↓ 捕获Selenium原生异常
# Selenium驱动层

class UIAutomationException(Exception):
    """UI自动化基础异常"""
    def __init__(self, message, context=None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)

class ElementOperationException(UIAutomationException):
    """元素操作异常"""
    pass

class PageStateException(UIAutomationException):
    """页面状态异常"""
    pass

class BusinessValidationException(UIAutomationException):
    """业务验证异常"""
    pass

class LoginFlowException(UIAutomationException):
    """登录流程异常"""
    pass

class DataPreparationException(UIAutomationException):
    """测试数据准备异常"""
    pass


def capture_exception_context(driver, operation_name, additional_context=None):
    """捕获异常时的上下文信息"""
    context = {
        "operation": operation_name,
        "timestamp": datetime.now().isoformat(),
        "current_url": driver.current_url,
        "page_title": driver.title,
        "window_size": driver.get_window_size(),
        "screenshot_path": None,
        "browser_logs": [],
        **additional_context
    }

    try:
        # 自动截图
        screenshot_path = f"screenshots/error_{operation_name}_{int(time.time())}.png"
        driver.save_screenshot(screenshot_path)
        context["screenshot_path"] = screenshot_path

        # 获取浏览器日志
        if driver.name.lower() == "chrome":
            context["browser_logs"] = driver.get_log("browser")

    except Exception as e:
        logger.warning(f"⚠️ 上下文信息收集失败: {str(e)}")

    return context



#


#推荐的做法（精确分类）
# try:
#     self.click_element(login_button)
# except ElementNotFoundException as e:
#     logger.error(f"❌ 元素未找到: {e.element_name}")
#     # 可以针对性地刷新页面重试
#     self.refresh_and_retry()
#
# except ElementNotClickableException as e:
#     logger.error(f"🚫 元素不可点击: {e.element_name}")
#     # 可以尝试JavaScript点击
#     self.js_click(e.locator)
#
# except TimeoutException as e:
#     logger.error(f"⏰ 操作超时: {e.operation}")
#     # 可以增加等待时间重试e