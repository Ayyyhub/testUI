import base64
from threading import Thread
import time
import glob
import os
import allure
from io import StringIO
from Log.logger import logger
from core.assertion import customed_assertion
from core.execute_test_data import UITestExecutor
from qwen_compare.context_helper import Context_Helper
from qwen_compare.opencv import screenshot_browser_content
from testcases.login_helper import LoginHelper
from testcases.newcreate_helper import NewcreateHelper
from utils.conf_reader import load_config
from utils.excell_reader import Excellreader

class Test_truework03:
    def __init__(self):
        self.driver = None  # 构造函数中初始化driver属性
        self.test_results = []  # 在 __init__ 中初始化
        self.current_sheet = ""  # 在 __init__ 中初始化
        self.ai_poll_threads = []  # 异步AI分析轮询线程列表
        self.pending_ai_attachments = []  # 存储待写入Allure的AI分析结果

    # 轮询AI分析结果的后台任务
    def poll_ai_analysis_result(self, folder, prefix, result_callback, max_wait_time=360, wait_interval=0.5):
        folder = os.path.abspath(folder)
        print(f"[DEBUG] 轮询目录: {folder}, 前缀: {prefix}")

        waited_time = 0
        ai_analysis_result = ""

        while waited_time < max_wait_time:
            # 找到以 prefix 开头的 txt
            files = [
                f for f in os.listdir(folder)
                if f.startswith(prefix) and f.endswith("_ai_result.txt")
            ]
            if files:
                files.sort(key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)
                newest_file = os.path.join(folder, files[0])
                print(f"[DEBUG] 😊 找到文件啦: {newest_file}")

                try:
                    with open(newest_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            ai_analysis_result = content
                            break
                except:
                    pass
            else:
                print(f"[DEBUG] 没有找到匹配的AI文件，等待中...")

            time.sleep(wait_interval)
            waited_time += wait_interval

        if not ai_analysis_result:
            ai_analysis_result = f"[AI超时] 超过 {max_wait_time}s 未发现有效AI结果文件"
            print(f"[DEBUG] {ai_analysis_result}")

        result_callback(ai_analysis_result)

    def test_truework03_func(self, driver):
        self.driver = driver
        self.test_results = []
        self.current_sheet = "PathGenerator"
        self.ai_poll_threads.clear()
        self.pending_ai_attachments.clear()

        # 登录
        test_login_example = LoginHelper()
        test_login_example.login_func(self.driver)

        # 新建
        new_create = NewcreateHelper()
        new_create.newcreate_func(self.driver)

        logger.info("\n"+"=== 开始执行work_flow03 ===\n")

        config = load_config()
        excell_reader = Excellreader(config["excell_path"])
        test_data_list3 = excell_reader.get_test_data(sheet_name=self.current_sheet)
        cs_assert = customed_assertion(self.driver)

        for data in test_data_list3:
            # get_context_data 获取上下文数据
            context_data_list = Context_Helper.get_context_data(data, test_data_list3, 2)
            if not data:
                continue
            print("\n" + "=" * 50)

            sio = StringIO()
            case_sink_id = logger.add(
                sio,
                level="INFO",
                enqueue=True,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[case]} | {extra[sheet]} | {extra[step]} - {message}",
            )
            bound_logger = logger.bind(case=data.test_case_id, sheet=self.current_sheet, step=data.step_id)
            bound_logger.info(f"执行测试用例：{data}")

            try:
                execute = UITestExecutor(self.driver)
                execute.execute_step(data)

                # ===== 判断断言方式 ======
                if data.assert_type == "visible":
                    # 断言成功
                    if cs_assert.assert_element_visible(data.assert_method, data.expected_result):
                        # 检查cv_points字段，如果为 TRUE 则 主动截屏！
                        if data.cv_points and str(data.cv_points).upper() == "TRUE":
                            try:
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                img = f"Proactive_{self.current_sheet}_{data.test_case_id}_{timestamp}.png"
                                print("⏳ 等待系统加载完成...")
                                time.sleep(3)
                                # 主动断言
                                screenshot_browser_content(img, self.driver)
                                Context_Helper.async_ai_comparison(img)
                            except Exception as screenshot_error:
                                print(f"❌ 主动截屏失败：{str(screenshot_error)}")

                        bound_logger.info(
                            f"断言成功，测试结果汇总：步骤 {data.step_id}: {data.status} - {data.outputed_result}")

                    # 断言失败
                    else:
                        try:
                            data.status = "FAIL"
                            data.outputed_result = f"断言失败：预期元素 {data.expected_result} 不可见"
                            print("断言失败准备截屏...")

                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                            img = f"AssertFailed_{self.current_sheet}_{data.test_case_id}_{timestamp}.png"

                            #opencv_screenshot(img, self.driver)
                            screenshot_browser_content(img, self.driver)

                            Context_Helper.async_ai_comparison(
                                screenshot_path=img,
                                current_data=data,
                                context_data_list=context_data_list
                            )
                        except Exception as screenshot_error:
                            # print(f"❌ 断言截屏失败：{str(screenshot_error)}")
                            bound_logger.error(f"断言截屏失败：{str(screenshot_error)}")

                elif data.assert_type == "closed":
                    if cs_assert.assert_popup_closed(data.assert_method, data.expected_result):
                        if data.cv_points and str(data.cv_points).upper() == "TRUE":
                            try:
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                img = f"Proactive_{self.current_sheet}_{data.test_case_id}_{timestamp}.png"
                                time.sleep(3)
                                # 主动断言
                                screenshot_browser_content(img, self.driver)
                                Context_Helper.async_ai_comparison(img)
                            except Exception as screenshot_error:
                                print(f"❌ 主动截屏失败：{str(screenshot_error)}")

                        bound_logger.info(
                            f"断言成功，测试结果汇总：步骤 {data.step_id}: {data.status} - {data.outputed_result}")

                    # 断言失败
                    else:
                        try:
                            data.status = "FAIL"
                            data.outputed_result = f"断言失败：预期元素 {data.expected_result} 不可见"
                            print("断言失败准备截屏...")

                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                            img = f"AssertFailed_{self.current_sheet}_{data.test_case_id}_{timestamp}.png"

                            #opencv_screenshot(img, self.driver)
                            screenshot_browser_content(img, self.driver)

                            Context_Helper.async_ai_comparison(
                                screenshot_path=img,
                                current_data=data,
                                context_data_list=context_data_list
                            )
                        except Exception as screenshot_error:
                            # print(f"❌ 断言截屏失败：{str(screenshot_error)}")
                            bound_logger.error(f"断言截屏失败：{str(screenshot_error)}")

            except Exception as e:
                
                bound_logger.exception("执行过程中发生异常{e}")
                data.status = "FAIL"
                data.outputed_result = "执行步骤异常"

            # ===================================================
            # 收集点击失败日志和断言日志
            # ===================================================
            click_logs = ""
            assert_logs = ""
            ai_analysis_holder = {"value": ""}
            record_holder = {"value": None}

            record = {
                "test_case_id": data.test_case_id,
                "description": data.description,
                "status": data.status,
                "sheet_name": self.current_sheet,
                "click_logs": click_logs,
                "assert_logs": assert_logs,
                "AI_analysis": ai_analysis_holder["value"],
                "screenshot_base64": "",
                "case_log_text":""
            }
            record_holder["value"] = record

            if data.status != "PASS":
                click_logs = f"执行失败日志：步骤 {data.step_id} - {data.outputed_result}"
                assert_logs = (
                    f"断言日志：步骤 {data.step_id} - "
                    f"预期：{data.expected_result}，实际结果：{data.outputed_result}"
                )

                # 闭包，回调函数！
                def update_ai_analysis_result(
                    result,
                    test_case_id=data.test_case_id,
                    ai_holder=ai_analysis_holder,
                    record_ref=record_holder,
                    pending_list=self.pending_ai_attachments

                ):
                    # # 使用闭包捕获的变量，如果参数为 None 则使用外部变量
                    # if test_case_id is None:
                    #     test_case_id = data.test_case_id
                    # if ai_holder is None:
                    #     ai_holder = ai_analysis_holder
                    # if record_ref is None:
                    #     record_ref = record_holder
                    # if pending_list is None:
                    #     pending_list = self.pending_ai_attachments

                    # with self.lock:
                    ai_holder["value"] = result
                    record = record_ref["value"]
                    if record is not None:
                        record["AI_analysis"] = result
                    pending_list.append((test_case_id, result))

                folder = "ai_comparison_results"
                # prefix = f"AssertFailed_{self.current_sheet}_{data.test_case_id}_"
                prefix = img.rsplit('.', 1)[0]

                ai_poll_thread = Thread(
                    target=self.poll_ai_analysis_result,
                    args=(folder,prefix,update_ai_analysis_result),
                    daemon=True
                )
                ai_poll_thread.start()
                self.ai_poll_threads.append(ai_poll_thread)

            # ===================================================
            # 截图处理
            # ===================================================
            screenshot_pattern = (
                f"screenshoot_dir/AssertFailed_{self.current_sheet}_{data.test_case_id}_*.png"
            )
            screenshot_files = glob.glob(screenshot_pattern)
            screenshot_base64 = ""

            if screenshot_files:
                screenshot_files.sort(key=os.path.getmtime, reverse=True)
                latest_screenshot = screenshot_files[0]
                try:
                    with open(latest_screenshot, 'rb') as f:
                        screenshot_data = f.read()
                        screenshot_base64 = base64.b64encode(
                            screenshot_data).decode('utf-8')
                except Exception as e:
                    print(f"截图读取失败：{str(e)}")

            record["screenshot_base64"] = screenshot_base64
            record["case_log_text"] = sio.getvalue()

            self.test_results.append(record)

            # 写入 步骤日志 到 Allure 附件
            try:
                allure.attach(
                    sio.getvalue(),
                    name=f"Log日志--{data.test_case_id}",
                    attachment_type=allure.attachment_type.TEXT
                )
            except Exception:
                pass
            logger.remove(case_sink_id)

        # 等待线程,确保所有线程都完成，再结束！
        for poll_thread in self.ai_poll_threads:
            if poll_thread.is_alive():
                poll_thread.join()
        self.ai_poll_threads.clear()

        # 写入 Allure
        for testcase_id, ai_text in self.pending_ai_attachments:
            try:
                allure.attach(
                    ai_text,
                    name=f"AI分析--{testcase_id}",
                    attachment_type=allure.attachment_type.TEXT
                )
            except Exception as attach_error:
                logger.info(f"Allure附件写入失败: {attach_error}")

        self.pending_ai_attachments.clear()

        return self.test_results
