# from selenium import webdriver
# import os
# import subprocess
# import yaml
#
# # 在 browser_engine.py 开头添加
# from selenium.webdriver.chrome.service import Service
#
#
# class BrowserEngine:
#
#     def __init__(self):
#         # 1. 获取当前脚本（browser_engine.py）的绝对路径
#         current_script_path = os.path.abspath(__file__)
#         # 2. 获取项目根目录（testUI 目录，假设 browser_engine.py 在 core 文件夹下）
#         project_root = os.path.dirname(os.path.dirname(current_script_path))
#         # 3. 拼接配置文件的绝对路径
#         config_file_path = os.path.join(project_root, "conf", "config.yaml")
#
#         # 4. 打开配置文件（此时路径一定正确）
#         with open(config_file_path, "r", encoding="utf-8") as f:
#             self.config = yaml.safe_load(f)
#
#     def initialize_driver(self):
#
#         # 初始化：杀死残留的chromedriver进程（避免旧会话冲突）
#         subprocess.run(
#             "taskkill /f /im chromedriver.exe",
#             shell=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#         )
#
#         """
#         初始化并返回Chrome浏览器驱动
#         """
#         chrome_driver_path = r"D:\ChromeDriver\chromedriver-win64\chromedriver-win64\chromedriver.exe"  # 修改为你的ChromeDriver实际路径
#         chrome_binary_path = (
#             r"D:\chrome-win64\chrome-win64\chrome.exe"
#         )
#
#         # 设置Chrome浏览器选项
#         options = webdriver.ChromeOptions()
#         # options.add_argument('--headless')  # 无头模式，如不需要可视化界面可注释
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.binary_location = chrome_binary_path  # 设置Chrome浏览器路径
#
#         # # 初始化浏览器驱动，使用旧版API方式, Selenium 版本（4.0+）已经移除了 executable_path 这个参数，
#         # driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
#
#         service = Service(
#             executable_path=chrome_driver_path
#         )  # 通过 Service 管理驱动路径
#         driver = webdriver.Chrome(service=service, options=options)
#         driver.maximize_window()
#
#         return driver


from selenium import webdriver
import os
import subprocess
import yaml
import platform
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class BrowserEngine:

    def __init__(self):
        current_script_path = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(current_script_path))
        config_file_path = os.path.join(project_root, "conf", "config.yaml")
        with open(config_file_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def initialize_driver(self):
        # 清理进程
        if platform.system().lower() == "windows":
            subprocess.run(
                "taskkill /f /im chromedriver.exe",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        else:
            subprocess.run(
                "pkill -f chromedriver",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        options = webdriver.ChromeOptions()

        # 环境检测：Jenkins 使用无头模式，本地保持可视化
        if os.getenv('JENKINS_HOME') or os.getenv('CI'):
            options.add_argument('--headless')
            print("运行在 CI 环境：启用无头模式")
        else:
            print("运行在本地环境：保持可视化界面")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        # 添加SSL相关配置以解决握手失败错误
        # options.add_argument("--ignore-certificate-errors")
        # options.add_argument("--ignore-ssl-errors")
        # options.add_argument("--disable-web-security")
        # options.add_argument("--allow-running-insecure-content")
        # options.add_argument("--disable-features=VizDisplayCompositor")
        # options.add_argument("--disable-gpu")
        # options.add_argument("--disable-software-rasterizer")
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)

        # 本地开发环境使用你现有的路径
        if platform.system().lower() == "windows" and not os.getenv('JENKINS_HOME'):
            chrome_driver_path = r"D:\ChromeDriver\chromedriver-win64\chromedriver-win64\chromedriver.exe"
            chrome_binary_path = r"D:\chrome-win64\chrome-win64\chrome.exe"
            options.binary_location = chrome_binary_path
            service = Service(executable_path=chrome_driver_path)
            print(f"使用本地 Chrome: {chrome_binary_path}")
            print(f"使用本地 ChromeDriver: {chrome_driver_path}")
        else:
            # Jenkins 环境使用 webdriver-manager 自动管理
            service = Service(ChromeDriverManager().install())
            print("使用 webdriver-manager 自动管理驱动")

        driver = webdriver.Chrome(service=service, options=options)

        # 打印版本信息用于验证
        browser_version = driver.capabilities['browserVersion']
        driver_version = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
        print(f"浏览器版本: {browser_version}")
        print(f"驱动版本: {driver_version}")

        driver.maximize_window()
        return driver