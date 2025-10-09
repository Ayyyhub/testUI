#测试夹具
from core.browser_engine import BrowserEngine
from core.logger import logger
from utils.excell_reader import Excellreader
import pytest
import time
from functools import wraps

# 增强版数据驱动装饰器
def data_provider(source, sheet_name='Sheet1'):
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(*args, **kwargs):
            test_data = Excellreader(source).read_data(sheet_name)
            for index, data in enumerate(test_data):
                logger.info(f"执行数据驱动测试第 {index+1} 组数据")
                try:
                    test_func(*args, **data, **kwargs)
                except AssertionError as e:
                    logger.error(f"第 {index+1} 组数据测试失败: {str(e)}")
                    raise
        return wrapper
    return decorator

# 带延迟的失败重试装饰器
def retry(attempts=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == attempts - 1:
                        raise
                    logger.warning(f"第 {i+1} 次重试，原因: {str(e)}")
                    time.sleep(delay)
        return wrapper
    return decorator

@pytest.fixture(scope="session")
def driver():
    """初始化浏览器驱动并返回driver实例"""
    browser_engine = BrowserEngine()
    driver = browser_engine.initialize_driver()
    yield driver
    driver.quit()

# # 增强版自动日志记录fixture
# @pytest.fixture(autouse=True)
# def auto_logger(request):
#     logger.info(f"开始执行测试用例: {request.node.name}")
#     start_time = time.time()
#     yield
#     duration = time.time() - start_time
#     logger.info(f"测试用例 {request.node.name} 执行完成，耗时: {duration:.2f}秒")