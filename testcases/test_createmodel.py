import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 导入init.py中的初始化函数
from core.browser_engine import BrowserEngine
from core.logger import logger  # 导入封装好的 logger


def set_x_length_by_css_hierarchy(driver):
    try:
        # 2. 逐层定位元素（从外层到内层）
        # 步骤1：定位最外层的 el-form-item 容器
        outer_form = driver.find_element(
            By.CSS_SELECTOR,
            "div.el-form-item.asterisk-left.el-form-item--label-right"
        )

        # 步骤2：在 outer_form 内，定位 el-form-item__content
        form_content = outer_form.find_element(
            By.CSS_SELECTOR,
            "div.el-form-item__content"
        )

        # 步骤3：在 form_content 内，定位 el-input-number
        input_number = form_content.find_element(
            By.CSS_SELECTOR,
            "div.el-input-number"
        )

        # 步骤4：在 input_number 内，定位 el-input
        el_input = input_number.find_element(
            By.CSS_SELECTOR,
            "div.el-input"
        )

        # 步骤5：在 el_input 内，定位目标输入框 el-input__inner
        target_input = el_input.find_element(
            By.CSS_SELECTOR,
            "input.el-input__inner"
        )

        # 3. 修改输入框的值为 2500
        target_input.clear()  # 清空原有值（若需保留可跳过）
        target_input.send_keys("2500")  # 输入新值

        # （可选）用 JavaScript 强制设置值（确保值被立即修改）
        # driver.execute_script("arguments[0].value = '2500';", target_input)

        # 验证结果（打印输入框当前值）
        print("输入框当前值：", target_input.get_attribute("value"))

    except Exception as e:
        print(f"定位过程出错：{e}")
    # finally:
    #     driver.quit()  # 无论是否出错，最终关闭浏览器




def test_createmodel_func(driver):
    try:
        logger.info("开始创建模型测试...")

        # browser_engine = BrowserEngine()
        # # 使用init.py中的函数初始化浏览器驱动
        # driver = browser_engine.initialize_driver()


        model=driver.find_element(By.XPATH,'//div[@class="collapse_item_title"]//span[text()="模型"]')
        model.click()

        # 使用当前浏览器实例查找创建模型按钮
        # 等待创建模型按钮出现
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="child_btns" and .//span="创建模型"]'))
        )
        create_model = driver.find_element(By.XPATH, '//div[@class="child_btns" and .//span="创建模型"]')
        print("找到创建模型按钮，点击...")
        create_model.click()

        #设置x长度
        set_x_length_by_css_hierarchy(driver)

        # 1. 先定位父容器
        parent_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.space-around.flex.margin"))
        )
        # # 2. 在父容器内定位“确定”按钮（注意XPath前加"."表示在当前元素内查找）
        # confirm_btn_in_parent = parent_div.find_element(By.XPATH, ".//button[text()='确定']")
        # confirm_btn_in_parent.click()
        # 再等父容器内的按钮可点击
        confirm_btn_in_parent = WebDriverWait(parent_div, 10).until(
            EC.element_to_be_clickable((By.XPATH, ".//button[.//span[text()='确定']]"))  # 修正XPath
        )
        confirm_btn_in_parent.click()
        time.sleep(3)
        # 尝试打印当前页面URL和标题，帮助调试
        print("当前页面URL:", driver.current_url)
        print("当前页面标题:", driver.title)


    except Exception as e:
        logger.error(f"创建模型测试失败: {e}")
        return False
