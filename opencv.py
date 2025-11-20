import cv2
import numpy as np
import pyautogui
import os
def opencv_screenshot(name, driver):
    try:
        # 构建完整的截图文件路径

        screenshot_dir = "screenshoot_dir"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        full_path = os.path.join(screenshot_dir, name)

        # 获取浏览器窗口位置和大小
        window_rect = driver.get_window_rect()

        # 计算网页内容区域（排除浏览器UI）
        browser_ui_height = 200

        # 计算有效内容区域
        content_x = window_rect['x']
        content_y = window_rect['y'] + browser_ui_height
        content_width = window_rect['width']
        content_height = window_rect['height'] - browser_ui_height

        # 截屏：使用pyautogui截取屏幕指定区域
        screenshot = pyautogui.screenshot(region=(
            content_x, content_y, content_width, content_height
        ))
        # 转换为OpenCV格式
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # 保存
        cv2.imwrite(full_path, screenshot_cv)

        print(f"   截屏成功：{full_path}")
        print(f"   截取区域：({content_x}, {content_y}) - {content_width}x{content_height}")

    except ImportError as e:
        # 如果OpenCV或pyautogui未安装，回退到Selenium截屏
        print(f"⚠️ OpenCV/pyautogui未安装，使用Selenium截屏：{e}")
        driver.save_screenshot(full_path)