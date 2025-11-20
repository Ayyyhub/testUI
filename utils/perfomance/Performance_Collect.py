import json
from datetime import datetime
from Log import logger


class PerformanceCollector:
    """性能数据收集器"""

    def __init__(self):
        self.performance_data = []

    def record_operation(
        self, operation_name, elapsed_ms, success=True, metadata=None
    ):
        """记录操作性能数据"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation_name,
            "elapsed_ms": elapsed_ms,
            "success": success,
            "metadata": metadata or {},
        }
        self.performance_data.append(record)
        return record

    def save_to_file(self, filename=None):
        """保存性能数据到文件"""
        if filename is None:
            filename = (
                f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.performance_data, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 性能数据已保存: {filename}")

    def get_statistics(self):
        """获取性能统计信息"""
        if not self.performance_data:
            return {}

        operations = {}
        for record in self.performance_data:
            op_name = record["operation"]
            if op_name not in operations:
                operations[op_name] = []
            operations[op_name].append(record["elapsed_ms"])

        stats = {}
        for op_name, times in operations.items():
            stats[op_name] = {
                "count": len(times),
                "avg_ms": sum(times) / len(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "p95_ms": (
                    sorted(times)[int(len(times) * 0.95)]
                    if len(times) > 1
                    else times[0]
                ),
            }

        return stats
