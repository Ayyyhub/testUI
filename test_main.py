import pytest

from core.browser_engine import BrowserEngine
from Log.logger import logger
from testcases.test_login import Test_login

from testcases.test_workflow01 import Test_truework01


def test_main(driver):

    """主测试流程"""

    try:
        # 1. 执行登录测试
        # print("=== 开始执行登录测试 ===")
        test_login_shili=Test_login()
        test_login_shili.test_login_func(driver)

        # test_upload_shili=Test_upload()
        # test_upload_shili.test_upload(driver)

        #2. 从excell开始truework
        test_truework_shili= Test_truework01()
        test_truework_shili.test_truework01_func(driver)

        logger.info("=== 所有测试执行完成 ===")

        # 询问用户是否关闭浏览器
        input("所有测试已完成，按Enter键关闭浏览器...")

    except Exception as e:
        logger.error(f"测试执行过程中发生错误: {e}")



if __name__ == "__main__":

    # pytest.main(["-s", "test_main.py", "--reruns", "1"])
    # pytest.main(["-s", "test_main.py"])
    # pytest.main(["-v", "--setup-show"]) #-v：详细输出（显示每个用例的执行结果）  #-s：显示测试用例中的 print 输出   #-k"关键词"：只执行函数名/类名包含关键词的用例   #-m"标记名"：只执行带有 @pytest.mark.标记名 的用例


    # 2、手动初始化 driver
    browser_engine = BrowserEngine()
    driver = browser_engine.initialize_driver()
    try:
        test_main(driver)  # 传入手动创建的 driver
    finally:
        driver.quit()  # 测试结束后关闭浏览器