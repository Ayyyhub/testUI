# # #日志封装
#
# from loguru import logger
# import os
# import sys  # 导入sys，用于控制台输出
#
#
#
# # 根据环境设置不同日志级别
# if os.getenv("ENVIRONMENT") == "DEBUG":
#     log_level = "DEBUG"  # 开发环境记录详细日志
# else:
#     log_level = "INFO"   # 生产环境只记录重要日志
#
# # 确保logs目录存在
# os.makedirs("Log/logs", exist_ok=True)
#
# # 配置【文件输出】
# logger.add(
#     "Log/logs/auto_test_{time:YYYY-MM-DD_HH-mm-ss}.log",
#     rotation="500 MB",
#     retention="7 days",
#     level=log_level,  # 动态级别
#     format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
#     encoding="utf-8"
# )
#
# # 配置【控制台输出】
# logger.add(
#     sys.stderr,  # 输出到标准错误流（控制台）
#
# #     level="INFO",  # 显示INFO及更高级别日志
# #     format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"  # 控制台日志格式（可简化）
# # )
#     level="DEBUG",  # 控制台显示所有日志
#     format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
# )
#
#
# # 导出logger供全局使用
# __all__ = ["logger"]


# #日志封装

from loguru import logger
import os
import sys  # 导入sys，用于控制台输出

# 使用全局变量确保处理器只被添加一次
_handlers_configured = False


def configure_logger():
    """配置日志处理器，确保只配置一次"""
    global _handlers_configured

    if _handlers_configured:
        return

    # 根据环境设置不同日志级别
    if os.getenv("ENVIRONMENT") == "DEBUG":
        log_level = "DEBUG"  # 开发环境记录详细日志
    else:
        log_level = "INFO"  # 生产环境只记录重要日志

    # 确保logs目录存在
    os.makedirs("Log/logs", exist_ok=True)

    # 配置【文件输出】
    logger.add(
        "Log/logs/ui_auto_test_{time:YYYY-MM-DD_HH-mm-ss}.log",
        rotation="500 MB",
        retention="7 days",
        level=log_level,  # 动态级别
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
        encoding="utf-8"
    )

    # # 配置【控制台输出】
    # logger.add(
    #     sys.stderr,  # 输出到标准错误流（控制台）
    #     level="DEBUG",  # 控制台显示所有日志
    #     format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    # )

    _handlers_configured = True


# 首次导入时自动配置
configure_logger()

# 导出logger供全局使用
__all__ = ["logger"]



