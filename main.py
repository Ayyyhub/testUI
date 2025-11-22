import sys
from AEUI_Bot import AEUIBot
from clean_specified_dir import cleanup_directories
from core.browser_engine import BrowserEngine
from Log.logger import logger

from testcases.test_workflow03 import Test_truework03

# 封装命令，保存结果至报告，发送消息至dingding
from utils.allure.allure_customed import (
    save_results_as_allure,
    send_dingtalk_message_with_report,
)


def run_main(browser_driver, is_allure_mode=False):
    """主测试流程
    Args:
        browser_driver: 浏览器驱动
        is_allure_mode: 是否为Allure模式，如果是则不在run_main中发送钉钉消息
    """
    try:
        logger.info("=== 调试信息：开始执行run_main函数 ===")

        # 清理截图文件和ai分析结果
        cleanup_directories()

        # 初始化钉钉机器人
        bot = AEUIBot()
        test_results_noallure = []

        # # 1. 从excell开始truework
        # logger.info("=== 调试信息：开始执行Test_truework01 ===")
        # test_truework_example = Test_truework01()
        # workflow01_results = test_truework_example.test_truework01_func(browser_driver)
        # # print(f"=== 调试信息：Test_truework01执行完成，结果：{workflow01_results} ===")
        # if workflow01_results:
        #     test_results_noallure.extend(workflow01_results)
        #     # print(f"=== 调试信息 workflow01_results的数据结构: {test_results_noallure}")

        # # 2. 运动副工作流
        # logger.info("=== 调试信息：开始执行Test_truework02 ===")
        # test_truework02_example = Test_truework02()
        # workflow02_results = test_truework02_example.test_truework02_func(
        #     browser_driver
        # )
        # # print(f"=== 调试信息：Test_truework02执行完成，结果：{workflow02_results} ===")
        # if workflow02_results:
        #     test_results_noallure.extend(workflow02_results)
        #     # print(f"=== 调试信息 workflow02_results的数据结构: {test_results_noallure}")

        # 3. 路径生成程序
        test_truework03_example = Test_truework03()
        workflow03_results = test_truework03_example.test_truework03_func(
            browser_driver
        )
        if workflow03_results:
            test_results_noallure.extend(workflow03_results)

        logger.info("=== 所有测试执行完成 ===")

        # === 在"非Allure模式"(手动执行)下才在run_main中发送钉钉消息，但是有问题！！！===
        if not is_allure_mode:
            # 发送总测试结果到钉钉
            # print(f"=== 调试信息：准备发送测试结果 ===")
            # print(f"收集到的测试结果数量：{len(all_test_results)}")
            # print(f"测试结果内容：{all_test_results}")
            if test_results_noallure:
                logger.info("开始调用send_test_results方法...")
                bot.send_test_results(test_results_noallure)
            else:
                logger.warning("没有收集到测试结果，跳过钉钉消息发送")

        return test_results_noallure

    except Exception as e:
        logger.error(f"测试执行过程中发生错误: {e}")
        return []


if __name__ == "__main__":
    # 检查是否包含Allure参数
    allure_args = [arg for arg in sys.argv if "alluredir" in arg]

    if allure_args:
        # 使用Allure模式运行
        logger.info("=== 使用Allure模式运行 ===")

        # 执行测试并收集结果
        browser_engine = BrowserEngine()
        driver = browser_engine.initialize_driver()

        try:
            # 执行测试（传递is_allure_mode=True参数，避免重复发送钉钉消息）
            test_results_toallure = run_main(driver, is_allure_mode=True)
            # print(f"\n=== 调试信息查看test_miansresults数据结构: {test_results_allure} ===\n")

            if test_results_toallure:
                # 将测试结果保存为Allure格式
                save_results_as_allure(test_results_toallure)

                # 在报告生成后发送钉钉消息
                send_dingtalk_message_with_report(test_results_toallure)
            else:
                logger.info("没有收集到测试结果，跳过报告生成和消息发送")

        except Exception as e:
            logger.info(f"❌ 测试执行过程中发生错误: {e}")
        finally:
            driver.quit()

    else:
        # 手动初始化 driver（原有逻辑）
        logger.info("=== 使用手动模式运行 ===")
        browser_engine = BrowserEngine()
        driver = browser_engine.initialize_driver()
        try:
            run_main(driver)
        finally:
            driver.quit()  # 测试结束后关闭浏览器
