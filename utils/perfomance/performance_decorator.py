import functools


import time
from Log.logger import logger
from utils.perfomance.performance_collect import PerformanceCollector

performance_collector = PerformanceCollector()

# 增强的性能监控————&装饰器&

def monitored_performancer(operation_name=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            op_name = operation_name or func.__name__

            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.time() - start_time) * 1000

                # 记录到收集器
                performance_collector.record_operation(
                    operation_name=op_name,
                    elapsed_ms=elapsed_ms,
                    success=True,
                    metadata={"args": str(args)[:100], "kwargs": str(kwargs)[:100]}
                )

                logger.debug(f"⏱️ {op_name}: {elapsed_ms:.2f}ms")
                return result

            except Exception as e:
                elapsed_ms = (time.time() - start_time) * 1000
                performance_collector.record_operation(
                    operation_name=op_name,
                    elapsed_ms=elapsed_ms,
                    success=False,
                    metadata={"error": str(e), "args": str(args)[:100]}
                )
                raise

        return wrapper

    return decorator