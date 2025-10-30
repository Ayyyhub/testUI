from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from Log.logger import logger
from core.browser_engine import BrowserEngine
from pages.base_page import set_x_length_by_css_hierarchy
from testcases.login_helper import Login_Helper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def createmodel_func(driver):
        #self.driver = driver  # 保存driver到实例，后续用self.driver,如果后续有其他方法在同一个类下，无需再传 driver 参数
        try:
            logger.info("开始创建模型测试...")

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

    createmodel_func(driver)  # 保留你原有的创建模型逻辑

    # 步骤1：先定位Canvas，确保页面已稳定（避免注入时机过早）
    canva = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "canvas#fullCanvas"))
    )
    time.sleep(1)  # 等待Canvas内部3D场景初始化

    # 步骤2：注入JS函数（绑定到window，确保全局可见）
    js_code = """
    // 绑定到window，确保后续调用能找到
    window.selectObjectInThreeJS = function(canvas, clientX, clientY) {
        const rect = canvas.getBoundingClientRect();
        // 转换为Three.js标准化设备坐标
        const x = (clientX - rect.left) / rect.width * 2 - 1;
        const y = -(clientY - rect.top) / rect.height * 2 + 1;

        try {
            // 检查Three.js核心对象是否存在（关键！）
            if (!window.THREE || !window.raycaster || !window.camera || !window.scene) {
                console.error("Three.js核心对象未找到，请确认命名");
                return false;
            }
            // 执行射线检测
            window.raycaster.setFromCamera(new THREE.Vector2(x, y), window.camera);
            const intersects = window.raycaster.intersectObjects(window.scene.children, true);

            if (intersects.length > 0) {
                // 触发选中（根据前端实际逻辑调整，示例：添加选中样式）
                intersects[0].object.material.color.set(0xff0000); // 示例：变红
                console.log("成功选中物体：", intersects[0].object.name);
                return true;
            } else {
                console.log("未检测到物体交点");
                return false;
            }
        } catch (e) {
            console.error("选中逻辑出错：", e);
            return false;
        }
    };
    """
    # 执行注入（确保无语法错误）
    driver.execute_script(js_code)

    # 步骤3：验证函数是否已注入成功（调试用）
    is_defined = driver.execute_script("return typeof window.selectObjectInThreeJS === 'function';")
    print("注入的函数是否已定义：", is_defined)  # 若为False，检查JS语法或注入时机

    # 步骤4：调用注入的函数（使用你的目标坐标）
    target_clientX = 708
    target_clientY = 440

    try:
        result = driver.execute_script("""
            const canvas = document.querySelector('canvas#fullCanvas');
            return window.selectObjectInThreeJS(canvas, arguments[0], arguments[1]);
        """, target_clientX, target_clientY)
        print("选中操作结果（是否命中物体）：", result)
    except Exception as e:
        print("调用选中函数失败：", e)

    input("所有测试已完成，按Enter键关闭浏览器...")
    driver.quit()

if __name__ == '__main__':
    canvas()