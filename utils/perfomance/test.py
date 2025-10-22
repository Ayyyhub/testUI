# from utils.perfomance.Performance_Class import PerformanceMonitor
# from utils.perfomance.performance_decorator import monitored_performance
#
#
# class shishi:
#     def __init__(self, driver):
#         self.driver = driver
#         self.monitor = PerformanceMonitor("登录流程")
#
#     @monitored_performance("输入用户名")
#     def input_username(self, username):
#         element = self.driver.find_element(*USERNAME_LOCATOR)
#         element.clear()
#         element.send_keys(username)
#
#     @monitored_performance("输入密码")
#     def input_password(self, password):
#         element = self.driver.find_element(*PASSWORD_LOCATOR)
#         element.clear()
#         element.send_keys(password)
#
#     @monitored_performance("点击登录按钮")
#     def click_login(self):
#         element = self.driver.find_element(*LOGIN_BUTTON_LOCATOR)
#         element.click()
#
#     def login(self, username, password):
#         # 详细监控整个流程
#         self.monitor.start()
#
#         self.input_username(username)
#         self.monitor.checkpoint("用户名输入完成")
#
#         self.input_password(password)
#         self.monitor.checkpoint("密码输入完成")
#
#         self.click_login()
#         self.monitor.checkpoint("登录点击完成")
#
#         # 等待登录结果
#         with performance_tracker("登录结果等待", warn_threshold=3000):
#             WebDriverWait(self.driver, 10).until(
#                 EC.url_contains("dashboard")
#             )
#
#         total_time = self.monitor.stop(warn_threshold=8000)
#         logger.info(f"🎯 登录流程总耗时: {total_time:.2f}ms")
#
#         return total_time