#import logging
import sys
import os

from core.browser_engine import BrowserEngine
from testcases.test_truework01 import Test_truework01
from utils.excell_reader import TestData
from utils.excell_reader import Excellreader, TestData
# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from testcases import test_login
from testcases import test_createmodel
from core.logger import logger
from testcases.test_newcreate import TestNewCreate  # 导入类，不是直接导入方法


def main():
    """主测试流程"""
    #driver = None
    browser_engine = BrowserEngine()
    # 使用init.py中的函数初始化浏览器驱动
    driver = browser_engine.initialize_driver()
    try:
        # 1. 执行登录测试
        logger.info("=== 开始执行登录测试 ===")
        test_login.test_login_func(driver)  # 这会返回浏览器驱动

        # 2. 执行创建模型测试（使用同一个driver）
        logger.info("=== 开始执行创建模型测试 ===")
        test_createmodel.test_createmodel_func(driver)

        # 3. 从excell点击新建
        logger.info("=== 开始执行点击创建功能 ===")
        #test_newcreate.test_new_create_func(driver)
        test_newcreate_shili = TestNewCreate()  # 实例化TestNewCreate类
        test_newcreate_shili.run_all_tests(driver)  # 调用实例方法

        #4. 从excell开始truework
        test_truework_shili= Test_truework01()
        test_truework_shili.test_truework01_func(driver)

        logger.info("=== 所有测试执行完成 ===")

        # 询问用户是否关闭浏览器
        input("所有测试已完成，按Enter键关闭浏览器...")

    except Exception as e:
        logger.error(f"测试执行过程中发生错误: {e}")
    # finally:
    #     if driver:
    #         driver.quit()
    #         logger.info("浏览器已关闭")


if __name__ == "__main__":
    main()