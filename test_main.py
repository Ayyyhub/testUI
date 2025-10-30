import pytest
import sys
import os
from AEUI_Bot import AEUIBot
from core.browser_engine import BrowserEngine
from Log.logger import logger
from testcases.login_helper import Login_Helper

from testcases.test_workflow01 import Test_truework01
from testcases.test_workflow02 import Test_truework02


def run_main(driver):

    """主测试流程"""
    try:
        print("=== 调试信息：开始执行run_main函数 ===")
        
        # 初始化钉钉机器人
        bot = AEUIBot()
        all_test_results = []
        
        #2. 从excell开始truework
        print("=== 调试信息：开始执行Test_truework01 ===")
        test_truework_example = Test_truework01()
        workflow01_results = test_truework_example.test_truework01_func(driver)
        print(f"=== 调试信息：Test_truework01执行完成，结果：{workflow01_results} ===")
        if workflow01_results:
            all_test_results.extend(workflow01_results)

        #3. 运动副工作流
        print("=== 调试信息：开始执行Test_truework02 ===")
        test_truework02_example = Test_truework02()
        workflow02_results = test_truework02_example.test_truework02_func(driver)
        print(f"=== 调试信息：Test_truework02执行完成，结果：{workflow02_results} ===")
        if workflow02_results:
            all_test_results.extend(workflow02_results)

        logger.info("=== 所有测试执行完成 ===")

        # 发送总测试结果到钉钉
        print(f"=== 调试信息：准备发送测试结果 ===")
        print(f"收集到的测试结果数量：{len(all_test_results)}")
        print(f"测试结果内容：{all_test_results}")
        
        if all_test_results:
            print("开始调用send_test_results方法...")
            bot.send_test_results(all_test_results)
        else:
            logger.warning("没有收集到测试结果，跳过钉钉消息发送")

        # 询问用户是否关闭浏览器
        input("所有测试已完成，按Enter键关闭浏览器...")

    except Exception as e:
        logger.error(f"测试执行过程中发生错误: {e}")



if __name__ == "__main__":

    # 1、pytest
    # pytest.main(["-s", "test_main.py", "--reruns", "1"])
    # 显示测试执行顺序 --setup-show
    # pytest.run_main(["-v", "--setup-show"]) #-v：详细输出（显示每个用例的执行结果）  #-s：显示测试用例中的 print 输出   #-k"关键词"：只执行函数名/类名包含关键词的用例   #-m"标记名"：只执行带有 @pytest.mark.标记名 的用例

    # # 2、手动初始化 driver
    # browser_engine = BrowserEngine()
    # driver = browser_engine.initialize_driver()
    # try:
    #     run_main(driver)  # 传入手动创建的 driver
    # finally:
    #     driver.quit()  # 测试结束后关闭浏览器

    # 检查是否包含Allure参数
    allure_args = [arg for arg in sys.argv if 'alluredir' in arg]
    
    if allure_args:
        # 使用pytest模式运行（支持Allure）
        print("=== 使用pytest模式运行，支持Allure报告生成 ===")
        
        # 将测试类转换为pytest测试用例
        import pytest
        
        # 创建pytest测试函数
        @pytest.fixture(scope="session")
        def driver():
            browser_engine = BrowserEngine()
            driver = browser_engine.initialize_driver()
            yield driver
            driver.quit()
        
        def test_main_workflow(driver):
            run_main(driver)
        
        # 运行pytest
        pytest.main(sys.argv[1:])
    else:
        # 手动初始化 driver（原有逻辑）
        print("=== 使用手动模式运行 ===")
        browser_engine = BrowserEngine()
        driver = browser_engine.initialize_driver()
        try:
            run_main(driver)  # 传入手动创建的 driver
        finally:
            driver.quit()  # 测试结束后关闭浏览器