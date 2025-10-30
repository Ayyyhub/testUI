from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from Log.logger import logger
from core.browser_engine import BrowserEngine
from testcases.login_helper import Login_Helper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def createmodel_func(driver):
    # self.driver = driver  # 保存driver到实例，后续用self.driver,如果后续有其他方法在同一个类下，无需再传 driver 参数
    try:
        logger.info("开始创建模型测试...")

        model = driver.find_element(By.XPATH, '//div[@class="collapse_item_title"]//span[text()="模型"]')
        model.click()

        # 使用当前浏览器实例查找创建模型按钮
        # 等待创建模型按钮出现
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="child_btns" and .//span="创建模型"]'))
        )
        create_model = driver.find_element(By.XPATH, '//div[@class="child_btns" and .//span="创建模型"]')
        print("找到创建模型按钮，点击...")
        create_model.click()

        # 设置x长度
        # set_x_length_by_css_hierarchy(driver)

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


def canvas():
    browser_engine = BrowserEngine()
    driver = browser_engine.initialize_driver()
    driver.maximize_window()
    time.sleep(2)

    test_login_example = Login_Helper()
    test_login_example.login_func(driver)

    createmodel_func(driver)

    # 步骤2：注入Three.js射线检测逻辑
    js_code = """
    function selectObjectInThreeJS(canvas, clientX, clientY) {
        const rect = canvas.getBoundingClientRect();
        const x = (clientX - rect.left) / canvas.clientWidth * 2 - 1;
        const y = -(clientY - rect.top) / canvas.clientHeight * 2 + 1;

        // 请与前端确认camera、raycaster、scene的全局变量命名！
        window.raycaster.setFromCamera(new THREE.Vector2(x, y), window.camera);
        const intersects = window.raycaster.intersectObjects(window.scene.children, true);

        if (intersects.length > 0) {
            intersects[0].object.selected = true; // 假设选中逻辑是设置selected属性
            console.log("选中物体：", intersects[0].object.name);
            return true;
        }
        return false;
    }
    """
    driver.execute_script(js_code)

    # 步骤3：执行注入的选中函数
    target_clientX = 708
    target_clientY = 467
    driver.execute_script("""
        const canvas = document.querySelector('canvas#fullCanvas');
        selectObjectInThreeJS(canvas, arguments[0], arguments[1]);
    """, target_clientX, target_clientY)

    input("所有测试已完成，按Enter键关闭浏览器...")
    driver.quit()


if __name__ == '__main__':
    canvas()