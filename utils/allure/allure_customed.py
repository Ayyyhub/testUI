import shutil
import os
import sys
import json
from datetime import datetime
from AEUI_Bot import AEUIBot
from core.browser_engine import BrowserEngine
import subprocess
import time
import threading



# """使用Allure运行测试"""
# def run_tests_with_allure():
#     print("=== 开始执行Allure测试 ===")
#
#     # 清理之前的测试结果
#     import shutil
#     if os.path.exists("./allure-results"):
#         shutil.rmtree("./allure-results")
#     if os.path.exists("./allure-report"):
#         shutil.rmtree("./allure-report")
#
#     # 创建测试结果目录
#     os.makedirs("./allure-results", exist_ok=True)
#
#     # 执行测试并收集结果
#     browser_engine = BrowserEngine()
#     driver = browser_engine.initialize_driver()
#     try:
#         # 执行测试并收集详细结果
#         test_results = run_main(driver)
#
#         # 将测试结果保存为Allure格式
#         save_results_as_allure(test_results)
#
#         return True
#     except Exception as e:
#         print(f"测试执行失败: {e}")
#         return False
#     finally:
#         driver.quit()


# """将测试结果保存为Allure格式"""
def save_results_as_allure(test_results):

    if not test_results:
        print("警告：没有测试结果数据，创建空的Allure报告")
        return

    # 清理之前的测试结果
    if os.path.exists("./allure-results"):
        shutil.rmtree("./allure-results")
    os.makedirs("./allure-results", exist_ok=True)

    # 计算每个工作流的偏移量，避免不同工作流的时间戳冲突
    workflow_offsets = {}
    current_offset = 0
    
    # 为每个工作流分配唯一的偏移量
    for test_case in test_results:
        sheet_name = test_case.get('sheet_name', '未知工作表')
        if sheet_name not in workflow_offsets:
            workflow_offsets[sheet_name] = current_offset
            # 假设每个工作流最多有1000个测试用例，预留足够的间隔
            current_offset += 1000000  # 1000秒间隔

    # 为每个测试用例创建详细的Allure结果
    case_counters = {}  # 记录每个工作流中的用例序号
    for i, test_case in enumerate(test_results):
        test_case_id = test_case.get('test_case_id', f'test-case-{i}')
        description = test_case.get('description', '无描述')
        status = test_case.get('status', 'unknown')
        sheet_name = test_case.get('sheet_name', '未知工作表')

        # 转换状态为Allure格式（正确处理各种状态）
        if status == "PASS":
            allure_status = "passed"
        elif status == "FAIL":
            allure_status = "failed"
        elif status == "ERROR":
            allure_status = "broken"
        else:
            allure_status = "unknown"

        # 更新工作流计数器（每个用例处理时都递增对应工作流的计数器）
        if sheet_name not in case_counters:
            case_counters[sheet_name] = 0  # 第一个用例序号为0
        else:
            case_counters[sheet_name] += 1  # 后续用例递增序号
        
        # 获取当前用例在该工作流中的序号
        case_index = case_counters[sheet_name]

        # 创建时间戳（确保每个测试用例有不同的时间，按执行顺序排列）
        # 使用工作流偏移量加上递增的偏移量，确保不同工作流之间不会冲突
        base_time = 1700000000000  # 使用固定的起始时间戳
        workflow_offset = workflow_offsets.get(sheet_name, 0)
        start_time = base_time + workflow_offset + case_index * 1000  # 每个用例间隔1秒
        stop_time = start_time + 500  # 每个用例执行0.5秒
        print(f"=== Allure调试：测试用例 {test_case['test_case_id']} 时间戳: {start_time} (工作流: {sheet_name}, 序号: {case_index})")

        # 创建详细的测试结果（符合Allure 2.0标准格式）
        allure_result = {
            "name": description,
            "status": allure_status,
            "statusDetails": {
                "known": False,
                "muted": False,
                "flaky": False,
                "message": "请查看Log日志..." if status != "PASS" else None,
                "trace": "请查看Log日志..." if status != "PASS" else None
            },
            "start": start_time,
            "stop": stop_time,
            "uuid": f"{test_case_id}-{sheet_name}-{case_index}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}-{hash(description)}",
            "historyId": test_case_id,
            "testCaseId": test_case_id,
            "fullName": f"{sheet_name} - {description}",
            "labels": [
                {"name": "suite", "value": sheet_name},
                {"name": "feature", "value": description},
                {"name": "story", "value": test_case_id},
                {"name": "severity", "value": "normal"},
                {"name": "framework", "value": "pytest"},
                {"name": "language", "value": "python"}
            ],
            "links": [],
            "parameters": [
                {"name": "工作表", "value": sheet_name},
                {"name": "用例ID", "value": test_case_id}
            ],
            "steps": [
                {
                    "name": "执行测试用例",
                    "status": allure_status,
                    "start": start_time,
                    "stop": stop_time,
                    "steps": []
                }
            ]
        }

        # 保存结果文件
        result_file = f"./allure-results/{allure_result['uuid']}-result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(allure_result, f, ensure_ascii=False, indent=2)

        print(f"✓ 保存Allure测试结果: {sheet_name} - {test_case_id} - {description} - {status} - 序号{case_index}")

    print(f"✓ 共保存 {len(test_results)} 个测试用例的Allure结果")

    # 创建一个环境信息文件
    environment_info = {
        "python_version": sys.version,
        "platform": sys.platform,
        "timestamp": datetime.now().isoformat()
    }

    with open("./allure-results/environment.properties", 'w', encoding='utf-8') as f:
        for key, value in environment_info.items():
            f.write(f"{key}={value}\n")

# def save_results_as_allure(test_results):
#     if not test_results:
#         print("警告：没有测试结果数据，创建空的Allure报告")
#         return
#
#     # 清理之前的测试结果
#     if os.path.exists("./allure-results"):
#         shutil.rmtree("./allure-results")
#     os.makedirs("./allure-results", exist_ok=True)
#
#     # 为每个测试用例创建详细的Allure结果
#     for i, test_case in enumerate(test_results):
#         test_case_id = test_case.get('test_case_id', f'test-case-{i}')
#         description = test_case.get('description', '无描述')
#         status = test_case.get('status', 'unknown')
#         sheet_name = test_case.get('sheet_name', '未知工作表')
#
#         # 转换状态为Allure格式
#         if status == "PASS":
#             allure_status = "passed"
#         elif status == "FAIL":
#             allure_status = "failed"
#         elif status == "ERROR":
#             allure_status = "broken"
#         else:
#             allure_status = "unknown"
#
#         # 使用全局索引确保时间戳顺序正确
#         base_time = 1700000000000
#         start_time = base_time + i * 1000  # 每个用例间隔1秒
#         stop_time = start_time + 500  # 每个用例执行0.5秒
#
#         print(f"=== Allure调试：测试用例 {test_case_id} 时间戳: {start_time} (全局序号: {i})")
#
#         # 创建详细的测试结果
#         allure_result = {
#             "name": description,
#             "status": allure_status,
#             "statusDetails": {
#                 "known": False,
#                 "muted": False,
#                 "flaky": False,
#                 "message": "请查看Log日志..." if status != "PASS" else None,
#                 "trace": "请查看Log日志..." if status != "PASS" else None
#             },
#             "start": start_time,
#             "stop": stop_time,
#             "uuid": f"{test_case_id}-{i}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
#             "historyId": test_case_id,
#             "testCaseId": test_case_id,
#             "fullName": f"{sheet_name} - {description}",
#             "labels": [
#                 {"name": "suite", "value": sheet_name},
#                 {"name": "feature", "value": description},
#                 {"name": "story", "value": test_case_id},
#                 {"name": "severity", "value": "normal"},
#                 {"name": "framework", "value": "pytest"},
#                 {"name": "language", "value": "python"}
#             ],
#             "links": [],
#             "parameters": [
#                 {"name": "工作表", "value": sheet_name},
#                 {"name": "用例ID", "value": test_case_id}
#             ],
#             "steps": [
#                 {
#                     "name": "执行测试用例",
#                     "status": allure_status,
#                     "start": start_time,
#                     "stop": stop_time,
#                     "steps": []
#                 }
#             ]
#         }
#
#         # 保存结果文件
#         result_file = f"./allure-results/{allure_result['uuid']}-result.json"
#         with open(result_file, 'w', encoding='utf-8') as f:
#             json.dump(allure_result, f, ensure_ascii=False, indent=2)
#
#         print(f"✓ 保存Allure测试结果: {sheet_name} - {test_case_id} - {status} - 全局序号{i}")
#
#     print(f"✓ 共保存 {len(test_results)} 个测试用例的Allure结果")
#
#     # 创建环境信息文件
#     environment_info = {
#         "python_version": sys.version,
#         "platform": sys.platform,
#         "timestamp": datetime.now().isoformat()
#     }
#
#     with open("./allure-results/environment.properties", 'w', encoding='utf-8') as f:
#         for key, value in environment_info.items():
#             f.write(f"{key}={value}\n")

# """生成Allure报告"""
def generate_allure_report():
    try:
        print("=== 开始生成Allure报告 ===")

        # 检查allure-results目录是否存在
        if not os.path.exists("./allure-results"):
            print("❌ 未找到测试结果目录: allure-results")
            return None

        # 检查allure-results目录中是否有文件
        result_files = [f for f in os.listdir("./allure-results") if f.endswith('.json')]
        if not result_files:
            print("❌ allure-results目录中没有测试结果文件")
            return None

        print(f"找到 {len(result_files)} 个测试结果文件")


        # 首先检查allure命令是否可用
        try:
            version_result = subprocess.run(
                ["allure", "--version"],
                capture_output=True,
                text=True,
                shell=True
            )

            if version_result.returncode == 0:
                print(f"✓ Allure版本: {version_result.stdout.strip()}")

                # 清理并生成报告（使用与手动命令相同的逻辑）
                result = subprocess.run([
                    "allure", "generate",
                    "./allure-results",
                    "-o", "./allure-report",
                    "--clean"
                ], capture_output=True, text=True, shell=True)

                if result.returncode == 0:
                    print("✓ Allure报告生成成功！")

                    # 启动本地HTTP服务器并返回URL
                    return start_allure_server()
                else:
                    print(f"❌ Allure报告生成失败: {result.stderr}")
                    return None

        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Allure命令行工具未安装")
            return None

    except Exception as e:
        print(f"❌ Allure报告生成过程中发生异常: {e}")
        return None


# """启动Allure本地服务器并返回可访问的URL"""
def start_allure_server():


    try:
        # 启动allure open命令（非阻塞方式）
        server_process = subprocess.Popen(
            ["allure", "open", "./allure-report", "-p", "8080"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )

        # 等待服务器启动
        time.sleep(3)

        # 检查服务器是否正常运行
        import requests
        try:
            response = requests.get("http://localhost:8080", timeout=5)
            if response.status_code == 200:
                allure_url = "http://localhost:8080"
                print(f"✓ Allure服务器已启动: {allure_url}")

                # 在后台保持服务器运行
                def keep_server_alive():
                    try:
                        server_process.wait()
                    except:
                        pass

                threading.Thread(target=keep_server_alive, daemon=True).start()

                return allure_url
        except:
            pass

        # 如果8080端口被占用，尝试其他端口
        for port in [8081, 8082, 8083, 8084]:
            try:
                server_process.terminate()
                server_process = subprocess.Popen(
                    ["allure", "open", "./allure-report", "-p", str(port)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True
                )

                time.sleep(3)

                try:
                    response = requests.get(f"http://localhost:{port}", timeout=5)
                    if response.status_code == 200:
                        allure_url = f"http://localhost:{port}"
                        print(f"✓ Allure服务器已启动: {allure_url}")

                        # 在后台保持服务器运行
                        threading.Thread(target=keep_server_alive, daemon=True).start()

                        return allure_url
                except:
                    continue

            except:
                continue

        print("⚠ 无法启动Allure服务器，将使用文件路径")
        return os.path.abspath("./allure-report/index.html")

    except Exception as e:
        print(f"❌ 启动Allure服务器失败: {e}")
        return os.path.abspath("./allure-report/index.html")


# """在Allure报告生成后发送钉钉消息"""
def send_dingtalk_message_with_report(test_results):
    import time

    # 先生成Allure报告并获取URL
    report_url = generate_allure_report()

    if report_url:
        print(f"✓ Allure报告生成成功，URL: {report_url}")

        # 发送钉钉消息（包含可点击的URL）
        bot = AEUIBot()
        if test_results:
            print("开始调用send_test_results方法...")
            # 传递报告URL给发送方法
            bot.send_test_results(test_results, report_url)
        else:
            print("没有测试结果，跳过钉钉消息发送")
    else:
        print("⚠ Allure报告生成失败，将发送不含报告链接的消息")
        bot = AEUIBot()
        if test_results:
            bot.send_test_results(test_results)