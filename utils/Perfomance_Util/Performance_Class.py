
# 性能监控类

class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.start_time = None
        self.checkpoints = {}

    def start(self):
        """开始监控"""
        self.start_time = time.time()
        self.checkpoints = {}
        logger.debug(f"⏱️ 开始监控: {self.operation_name}")
        return self

    def checkpoint(self, checkpoint_name):
        """记录检查点时间"""
        if self.start_time is None:
            raise RuntimeError("监控未开始，请先调用start()")

        current_time = time.time()
        elapsed_ms = (current_time - self.start_time) * 1000
        self.checkpoints[checkpoint_name] = elapsed_ms
        logger.debug(f"📍 检查点 - {self.operation_name}.{checkpoint_name}: {elapsed_ms:.2f}ms")

    def stop(self, warn_threshold=5000, error_threshold=10000):
        """停止监控并报告"""
        if self.start_time is None:
            raise RuntimeError("监控未开始，请先调用start()")

        total_elapsed_ms = (time.time() - self.start_time) * 1000

        # 生成详细报告
        report = self._generate_report(total_elapsed_ms)

        # 根据总耗时记录日志
        if total_elapsed_ms >= error_threshold:
            logger.error(f"🚨 性能异常 - {self.operation_name}\n{report}")
        elif total_elapsed_ms >= warn_threshold:
            logger.warning(f"⚠️ 性能警告 - {self.operation_name}\n{report}")
        else:
            logger.debug(f"✅ 性能正常 - {self.operation_name}\n{report}")

        return total_elapsed_ms

    def _generate_report(self, total_time):
        """生成性能报告"""
        report_lines = [f"总耗时: {total_time:.2f}ms"]

        if self.checkpoints:
            previous_time = 0
            for checkpoint, time_ms in self.checkpoints.items():
                segment_time = time_ms - previous_time
                percentage = (segment_time / total_time) * 100 if total_time > 0 else 0
                report_lines.append(f"  ├─ {checkpoint}: {time_ms:.2f}ms (+{segment_time:.2f}ms, {percentage:.1f}%)")
                previous_time = time_ms

        return "\n".join(report_lines)


def generate_performance_report():
    """生成性能报告"""
    stats = performance_collector.get_statistics()

    if not stats:
        logger.info("📊 暂无性能数据")
        return

    logger.info("📈 ========== 性能分析报告 ==========")

    # 按平均耗时排序
    sorted_ops = sorted(stats.items(), key=lambda x: x[1]['avg_ms'], reverse=True)

    for op_name, op_stats in sorted_ops:
        logger.info(f"""
📊 操作: {op_name}
   ├─ 执行次数: {op_stats['count']}
   ├─ 平均耗时: {op_stats['avg_ms']:.2f}ms
   ├─ 最小耗时: {op_stats['min_ms']:.2f}ms  
   ├─ 最大耗时: {op_stats['max_ms']:.2f}ms
   └─ P95耗时: {op_stats['p95_ms']:.2f}ms
""")

    # 识别性能瓶颈
    bottlenecks = [(op, data) for op, data in sorted_ops if data['avg_ms'] > 1000]
    if bottlenecks:
        logger.warning("🚨 发现性能瓶颈:")
        for op_name, op_stats in bottlenecks[:3]:  # 只显示前3个
            logger.warning(f"   ⚠️ {op_name}: {op_stats['avg_ms']:.2f}ms")

    # 保存详细数据
    performance_collector.save_to_file()




# 使用示例
def detailed_workflow(self):
    monitor = PerformanceMonitor("详细工作流").start()

    # 步骤1
    self.step1()
    monitor.checkpoint("步骤1完成")

    # 步骤2
    self.step2()
    monitor.checkpoint("步骤2完成")

    # 步骤3
    self.step3()
    monitor.checkpoint("步骤3完成")

    # 结束监控
    total_time = monitor.stop(warn_threshold=15000)
    return total_time