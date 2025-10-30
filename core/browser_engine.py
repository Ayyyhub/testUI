from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import subprocess
import yaml
# 在 browser_engine.py 开头添加
from selenium.webdriver.chrome.service import Service

class BrowserEngine:


    def __init__(self):
        # 1. 获取当前脚本（browser_engine.py）的绝对路径
        current_script_path = os.path.abspath(__file__)
        # 2. 获取项目根目录（testUI 目录，假设 browser_engine.py 在 core 文件夹下）
        project_root = os.path.dirname(os.path.dirname(current_script_path))
        # 3. 拼接配置文件的绝对路径
        config_file_path = os.path.join(project_root, "conf", "config.yaml")

        # 4. 打开配置文件（此时路径一定正确）
        with open(config_file_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)



    def initialize_driver(self):

        # 初始化：杀死残留的chromedriver进程（避免旧会话冲突）
        subprocess.run("taskkill /f /im chromedriver.exe", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        """
        初始化并返回Chrome浏览器驱动
        """
        chrome_driver_path = r"D:\ChromeDriver\chromedriver-win64\chromedriver-win64\chromedriver.exe"  # 修改为你的ChromeDriver实际路径
        chrome_binary_path = r"D:\chrome-win64\chrome-win64\chrome.exe"  # 常见默认路径

        # 设置Chrome浏览器选项
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # 无头模式，如果需要可视化界面请注释掉这行
        # options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.binary_location = chrome_binary_path  # 设置Chrome浏览器路径

        # # 初始化浏览器驱动，使用旧版API方式, Selenium 版本（4.0+）已经移除了 executable_path 这个参数，
        # driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)

        service = Service(executable_path=chrome_driver_path)  # 通过 Service 管理驱动路径
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()

        return driver