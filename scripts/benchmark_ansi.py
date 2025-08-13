# By copilot

#!/usr/bin/env python3
"""
ANSI转义序列性能基准测试
比较 ESC[1K 和 ESC[2K 的性能差异
"""

import time
import sys
import os
from typing import List, Tuple


def benchmark_ansi_sequences(iterations: int = 10000) -> Tuple[float, float]:
    """
    基准测试ANSI转义序列的性能

    Args:
        iterations: 测试迭代次数

    Returns:
        Tuple[float, float]: (ESC[1K时间, ESC[2K时间)
    """

    # 准备测试数据
    test_content = "Test content for ANSI escape sequence benchmark " * 10

    # 测试 ESC[1K (清除到行首)
    print("Testing ESC[1K (clear to beginning of line)...")
    start_time = time.perf_counter()

    for i in range(iterations):
        # 模拟实际使用场景：输出内容然后清除
        print(f"\x1b[1K\r{test_content} {i}", end="", flush=False)

    # 强制刷新缓冲区
    sys.stdout.flush()
    esc1k_time = time.perf_counter() - start_time

    # 清理终端
    print("\x1b[1K\r", end="")

    # 测试 ESC[2K (清除整行)
    print("Testing ESC[2K (clear entire line)...")
    start_time = time.perf_counter()

    for i in range(iterations):
        # 模拟实际使用场景：输出内容然后清除
        print(f"\x1b[2K\r{test_content} {i}", end="", flush=False)

    # 强制刷新缓冲区
    sys.stdout.flush()
    esc2k_time = time.perf_counter() - start_time

    # 清理终端
    print("\x1b[2K\r", end="")

    return esc1k_time, esc2k_time


def benchmark_without_ansi(iterations: int = 10000) -> float:
    """
    基准测试不使用ANSI序列的性能（作为对照组）

    Args:
        iterations: 测试迭代次数

    Returns:
        float: 执行时间
    """

    test_content = "Test content for baseline benchmark " * 10

    print("Testing baseline (no ANSI sequences)...")
    start_time = time.perf_counter()

    # 重定向到空设备以避免实际输出
    original_stdout = sys.stdout

    try:
        # 在Windows上使用NUL，在Unix系统上使用/dev/null
        null_device = "NUL" if os.name == "nt" else "/dev/null"
        with open(null_device, "w") as devnull:
            sys.stdout = devnull

            for i in range(iterations):
                print(f"{test_content} {i}")
    finally:
        sys.stdout = original_stdout

    baseline_time = time.perf_counter() - start_time

    return baseline_time


def benchmark_memory_usage():
    """测试不同ANSI序列的内存使用情况"""
    import tracemalloc

    iterations = 1000
    test_content = "Memory test content " * 20

    # 测试ESC[1K内存使用
    tracemalloc.start()

    for i in range(iterations):
        output = f"\x1b[1K\r{test_content} {i}"
        # 模拟字符串操作
        _ = len(output)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    esc1k_memory = peak

    # 测试ESC[2K内存使用
    tracemalloc.start()

    for i in range(iterations):
        output = f"\x1b[2K\r{test_content} {i}"
        # 模拟字符串操作
        _ = len(output)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    esc2k_memory = peak

    return esc1k_memory, esc2k_memory


def run_comprehensive_benchmark():
    """运行综合基准测试"""

    print("=" * 60)
    print("ANSI转义序列性能基准测试")
    print("=" * 60)
    print()

    # 不同的测试规模
    test_scales = [1000, 5000, 10000, 50000]

    results = []

    for scale in test_scales:
        print(f"测试规模: {scale:,} 次迭代")
        print("-" * 40)

        # 运行基准测试
        esc1k_time, esc2k_time = benchmark_ansi_sequences(scale)
        baseline_time = benchmark_without_ansi(scale)

        # 计算相对性能
        esc1k_overhead = (
            ((esc1k_time - baseline_time) / baseline_time) * 100
            if baseline_time > 0
            else 0
        )
        esc2k_overhead = (
            ((esc2k_time - baseline_time) / baseline_time) * 100
            if baseline_time > 0
            else 0
        )

        results.append(
            {
                "scale": scale,
                "esc1k_time": esc1k_time,
                "esc2k_time": esc2k_time,
                "baseline_time": baseline_time,
                "esc1k_overhead": esc1k_overhead,
                "esc2k_overhead": esc2k_overhead,
            }
        )

        print(f"基准时间 (无ANSI):     {baseline_time:.6f} 秒")
        print(
            f"ESC[1K 时间:          {esc1k_time:.6f} 秒 (开销: {esc1k_overhead:+.2f}%)"
        )
        print(
            f"ESC[2K 时间:          {esc2k_time:.6f} 秒 (开销: {esc2k_overhead:+.2f}%)"
        )

        if esc1k_time > 0 and esc2k_time > 0:
            ratio = esc2k_time / esc1k_time
            print(f"ESC[2K] / ESC[1K] 比率: {ratio:.4f}")

            if ratio > 1.01:
                print(f"ESC[1K] 比 ESC[2K] 快 {((ratio - 1) * 100):.2f}%")
            elif ratio < 0.99:
                print(f"ESC[2K] 比 ESC[1K] 快 {((1/ratio - 1) * 100):.2f}%")
            else:
                print("性能几乎相同")

        print()

    # 内存使用测试
    print("内存使用测试")
    print("-" * 40)
    esc1k_memory, esc2k_memory = benchmark_memory_usage()
    print(f"ESC[1K] 内存峰值: {esc1k_memory:,} 字节")
    print(f"ESC[2K] 内存峰值: {esc2k_memory:,} 字节")
    print(f"内存差异: {abs(esc2k_memory - esc1k_memory):,} 字节")
    print()

    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)

    avg_esc1k_time = sum(r["esc1k_time"] for r in results) / len(results)
    avg_esc2k_time = sum(r["esc2k_time"] for r in results) / len(results)
    avg_ratio = avg_esc2k_time / avg_esc1k_time if avg_esc1k_time > 0 else 1

    print(f"平均ESC[1K]时间: {avg_esc1k_time:.6f} 秒")
    print(f"平均ESC[2K]时间: {avg_esc2k_time:.6f} 秒")
    print(f"平均性能比率:   {avg_ratio:.4f}")

    if abs(avg_ratio - 1) < 0.05:  # 5% 阈值
        print("\n结论: ESC[1K] 和 ESC[2K] 的性能差异可以忽略不计")
    elif avg_ratio > 1:
        print(f"\n结论: ESC[1K] 平均比 ESC[2K] 快 {((avg_ratio - 1) * 100):.2f}%")
    else:
        print(f"\n结论: ESC[2K] 平均比 ESC[1K] 快 {((1/avg_ratio - 1) * 100):.2f}%")

    print("\n建议:")
    print("- 对于您的应用场景，性能差异微不足道")
    print("- 选择应该基于功能需求而非性能考虑")
    print("- ESC[1K]: 适合已知光标位置的场景")
    print("- ESC[2K]: 适合需要确保整行清空的场景")


if __name__ == "__main__":
    try:
        run_comprehensive_benchmark()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        sys.exit(1)
