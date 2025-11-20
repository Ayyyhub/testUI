from Log import logger
from utils.perfomance.performance_collect import PerformanceCollector


def generate_performance_report():
    """生成性能报告"""
    stats = PerformanceCollector.get_statistics()

    if not stats:
        logger.info("📊 暂无性能数据")
        return

    logger.info("📈 ========== 性能分析报告 ==========")

    # 按平均耗时排序
    sorted_ops = sorted(
        stats.items(), key=lambda x: x[1]["avg_ms"], reverse=True
    )

    for op_name, op_stats in sorted_ops:
        logger.info(
            f"""
📊 操作: {op_name}
   ├─ 执行次数: {op_stats['count']}
   ├─ 平均耗时: {op_stats['avg_ms']:.2f}ms
   ├─ 最小耗时: {op_stats['min_ms']:.2f}ms
   ├─ 最大耗时: {op_stats['max_ms']:.2f}ms
   └─ P95耗时: {op_stats['p95_ms']:.2f}ms
"""
        )

    # 识别性能瓶颈
    bottlenecks = [
        (op, data) for op, data in sorted_ops if data["avg_ms"] > 1000
    ]
    if bottlenecks:
        logger.warning("🚨 发现性能瓶颈:")
        for op_name, op_stats in bottlenecks[:3]:  # 只显示前3个
            logger.warning(f"   ⚠️ {op_name}: {op_stats['avg_ms']:.2f}ms")

    # 保存详细数据
    PerformanceCollector.save_to_file()
