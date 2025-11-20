import shutil
import os
import sys
import json
from datetime import datetime
from AEUI_Bot import AEUIBot
import subprocess
import time
import socket
import glob



"""将测试结果保存为Allure格式"""
def save_results_as_allure(test_results):
    if not test_results:
        print("警告：没有测试结果数据，创建空的Allure报告")
        return

    print(f"=== SUITE调试: 开始处理 {len(test_results)} 个测试用例")

    # 分析Suite分布
    suite_distribution = {}
    for test_case in test_results:
        sheet_name = test_case.get("sheet_name", "未知工作表")
        suite_distribution[sheet_name] = (
            suite_distribution.get(sheet_name, 0) + 1
        )

    print("=== SUITE分布统计:")
    for suite, count in suite_distribution.items():
        print(f"    {suite}: {count} 个用例")

    # 清理之前的测试结果
    if os.path.exists("./allure-results"):
        shutil.rmtree("./allure-results")
    os.makedirs("./allure-results", exist_ok=True)

    # 为每个工作流分配唯一的偏移量
    workflow_offsets = {}
    current_offset = 0
    for test_case in test_results:
        sheet_name = test_case.get("sheet_name", "未知工作表")
        if sheet_name not in workflow_offsets:
            workflow_offsets[sheet_name] = current_offset
            current_offset += 1000000

    print(f"=== SUITE偏移量配置: {workflow_offsets}")

    # 为每个测试用例创建详细的Allure结果
    case_counters = {}
    suite_files = {}  # 按suite记录文件

    for i, test_case in enumerate(test_results):
        test_case_id = test_case.get("test_case_id", f"test-case-{i}")
        description = test_case.get("description", "无描述")
        status = test_case.get("status", "unknown")
        sheet_name = test_case.get("sheet_name", "未知工作表")

        # 状态转换
        if status == "PASS":
            allure_status = "passed"
        elif status == "FAIL":
            allure_status = "failed"
        elif status == "ERROR":
            allure_status = "broken"
        else:
            allure_status = "unknown"

        # 更新计数器
        if sheet_name not in case_counters:
            case_counters[sheet_name] = 0
        else:
            case_counters[sheet_name] += 1

        case_index = case_counters[sheet_name]

        # 时间戳计算
        base_time = 1700000000000
        workflow_offset = workflow_offsets.get(sheet_name, 0)
        start_time = base_time + workflow_offset + case_index * 1000
        stop_time = start_time + 500

        # 创建唯一标识符 ！
        unique_test_id = f"{sheet_name}_{test_case_id}"

        current_time = int(time.time() * 1000000)
        unique_uuid = f"{sheet_name}-{test_case_id}-{current_time}"

        print(f"=== SUITE处理: [{sheet_name}] -> {test_case_id}")
        print(f"    UUID: {unique_uuid}")
        print(f"    historyId: {unique_test_id}")

        # 创建测试结果 - 特别注意labels结构
        allure_result = {
            "name": f"{test_case_id}: {description}",
            "status": allure_status,
            "statusDetails": {
                "known": False,
                "muted": False,
                "flaky": False,
                "message": "请查看Log日志..." if status != "PASS" else None,
                "trace": "请查看Log日志..." if status != "PASS" else None,
            },
            "start": start_time,
            "stop": stop_time,
            "uuid": unique_uuid,
            "historyId": unique_test_id,  # 必须唯一，否则会覆盖
            "testCaseId": unique_test_id,  # 必须唯一，否则会覆盖
            "fullName": f"{sheet_name}.{test_case_id}",
            "labels": [
                # Suite相关标签 - 控制层级结构
                {"name": "suite", "value": sheet_name},
                {"name": "feature", "value": description},
                {"name": "story", "value": unique_test_id},
                # 其他标签
                {"name": "severity", "value": "normal"},
                {"name": "framework", "value": "pytest"},
                {"name": "language", "value": "python"},
                {"name": "package", "value": f"tests.{sheet_name}"},
            ],
            "links": [],
            "parameters": [
                {"name": "工作表", "value": sheet_name},
                {"name": "用例ID", "value": test_case_id},
            ],
            "steps": [
                {
                    "name": f"执行{test_case_id}",
                    "status": allure_status,
                    "start": start_time,
                    "stop": stop_time,
                    "steps": [],
                }
            ],
        }
        # 保存文件
        result_file = f"./allure-results/{unique_uuid}-result.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(allure_result, f, ensure_ascii=False, indent=2)

        # 记录suite文件统计
        if sheet_name not in suite_files:
            suite_files[sheet_name] = []
        suite_files[sheet_name].append(result_file)

        print(f"✓ 保存到Suite [{sheet_name}]: {test_case_id}")

    # 最终统计
    print("\n=== SUITE最终统计 ===")
    total_files = 0
    for suite, files in suite_files.items():
        print(f"Suite [{suite}]: {len(files)} 个文件")
        total_files += len(files)

    print(f"总文件数: {total_files}")
    print(f"期望文件数: {len(test_results)}")

    actual_files = glob.glob("./allure-results/*-result.json")
    print(f"实际生成文件数: {len(actual_files)}")

    if len(actual_files) != len(test_results):
        print("⚠️ 警告: 文件数量不匹配! 可能存在覆盖")
        # 列出所有生成的文件
        print("生成的文件列表:")
        for file in actual_files:
            print(f"  {file}")

    # 环境信息文件
    environment_info = {
        "python_version": sys.version,
        "platform": sys.platform,
        "timestamp": datetime.now().isoformat(),
    }

    with open(
        "./allure-results/environment.properties", "w", encoding="utf-8"
    ) as f:
        for key, value in environment_info.items():
            f.write(f"{key}={value}\n")


"""生成Allure报告"""
def generate_allure_report():
    try:
        print("=== 开始生成Allure报告 ===")

        # 检查allure-results目录是否存在
        if not os.path.exists("./allure-results"):
            print("❌ 未找到测试结果目录: allure-results")
            return None

        # 检查allure-results目录中是否有文件
        result_files = [
            f for f in os.listdir("./allure-results") if f.endswith(".json")
        ]
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
                shell=True,
            )

            if version_result.returncode == 0:
                print(f"✓ Allure版本: {version_result.stdout.strip()}")

                # 清理并生成报告（使用与手动命令相同的逻辑）
                result = subprocess.run(
                    [
                        "allure",
                        "generate",
                        "./allure-results",
                        "-o",
                        "./allure-report",
                        "--clean",
                    ],
                    capture_output=True,
                    text=True,
                    shell=True,
                )

                if result.returncode == 0:
                    print("✓ Allure报告生成成功！")

                    # 直接使用allure open命令启动服务器并获取URL
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


"""启动Allure本地服务器并返回可访问的URL"""
def find_available_port(start_port=8080, max_attempts=50):
    """查找可用的端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return port
        except OSError:
            continue
    return start_port  # 如果都不可用，返回起始端口

"""启动Allure服务器，自动处理端口占用"""
def start_allure_server():

    try:
        if not os.path.exists("./allure-report"):
            print("❌ 未找到allure-report目录")
            return None

        print("🚀 启动Allure报告服务器...")

        # 查找可用端口
        port = find_available_port(8080)

        # 使用指定端口启动allure
        _process = subprocess.Popen(
            ["allure", "open", "./allure-report", "-p", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
        )

        # 获取本机IP
        def get_local_ip():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except:
                return "localhost"

        local_ip = get_local_ip()

        # 等待服务器启动
        time.sleep(3)

        # 构建URL
        url = f"http://{local_ip}:{port}"

        print(f"✅ Allure服务器已启动在端口 {port}")
        print(f"📍 本地访问: http://localhost:{port}")
        print(f"🌐 远程访问: {url}")
        print("💡 请确保防火墙已开放相应端口")

        return url

    except Exception as e:
        print(f"❌ 启动Allure服务器时发生异常: {e}")
        return "Allure服务器启动异常"


"""在Allure报告生成后发送钉钉消息"""
def send_dingtalk_message_with_report(test_results):

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


# # 运行测试
# python test_main.py -v --alluredir=./allure-results
#
# # 生成报告 -o: output
# allure generate ./allure-results -o ./allure-report --clean
#
# # 打开报告
# allure open ./allure-report
