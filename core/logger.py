# #日志封装

from loguru import logger
import os
import sys  # 导入sys，用于控制台输出
#
# # 确保logs目录存在
# os.makedirs("logs", exist_ok=True)
#
# # 配置日志
# logger.add(
#     "logs/auto_test_{time:YYYY-MM-DD}.log",
#     rotation="500 MB",  # 文件过大自动轮转
#     retention="7 days",  # 保留最近7天的日志文件，超过则自动删除
#     level="INFO",
#     format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
#     encoding="utf-8"
# )
#
# # 导出logger供全局使用
# __all__ = ["logger"]





# 确保logs目录存在
os.makedirs(name="logs", exist_ok=True)

# 配置【文件输出】
logger.add(
    "logs/auto_test_{time:YYYY-MM-DD}.log",
    rotation="500 MB",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
    encoding="utf-8"
)

# 新增：配置【控制台输出】
logger.add(
    sys.stderr,  # 输出到标准错误流（控制台）
    level="INFO",  # 显示INFO及更高级别日志
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"  # 控制台日志格式（可简化）
)

# 导出logger供全局使用
__all__ = ["logger"]