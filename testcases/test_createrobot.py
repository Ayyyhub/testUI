



from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_createrobot_func(driver):
    # 初始化浏览器
    driver = webdriver.Chrome()
    driver.get("目标页面URL")  # 替换为实际页面地址

    try:
        # 定位并等待"打开"菜单元素可点击
        # 定位逻辑：匹配class为el-menu-item的li，且其内部包含文本为"打开"的span
        open_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//li[@class='el-menu-item' and .//span[text()='打开']]"
            ))
        )

        # 执行点击操作
        open_menu.click()
        print("成功点击'打开'菜单")

    except Exception as e:
        print(f"定位或点击失败：{e}")

    # finally:
    #     # 关闭浏览器（实际测试中可根据需要保留）
    #     driver.quit()
