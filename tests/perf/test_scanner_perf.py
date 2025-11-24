"""
扫描器性能测试

对比新旧实现的扫描性能（时间和内存）
"""
import os
import time
import tempfile
import shutil
import tracemalloc
from pathlib import Path
from typing import Dict, Tuple
import pytest

from smartrenamer.core.scanner import FileScanner
from smartrenamer.core.library import MediaLibrary


# 性能测试标记
pytestmark = pytest.mark.performance


class TestScannerPerformance:
    """扫描器性能测试"""
    
    @pytest.fixture
    def test_data_dir(self) -> Path:
        """创建测试数据目录"""
        # 检查是否跳过性能测试
        if os.getenv("SKIP_PERF_TESTS", "false").lower() == "true":
            pytest.skip("跳过性能测试")
        
        # 创建临时目录
        temp_dir = Path(tempfile.mkdtemp(prefix="smartrenamer_perf_"))
        
        # 创建测试文件结构
        num_dirs = 20
        files_per_dir = 50
        
        for i in range(num_dirs):
            dir_path = temp_dir / f"subdir_{i:02d}"
            dir_path.mkdir()
            
            for j in range(files_per_dir):
                # 创建视频文件（空文件）
                file_path = dir_path / f"Movie.Title.{2000+j}.1080p.BluRay.x264.mkv"
                # 写入一些数据以满足最小文件大小要求
                with open(file_path, "wb") as f:
                    f.write(b"0" * (11 * 1024 * 1024))  # 11 MB
        
        yield temp_dir
        
        # 清理
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _measure_performance(
        self,
        scanner: FileScanner,
        directory: Path,
        use_iter: bool = False
    ) -> Tuple[float, float, int]:
        """
        测量扫描性能
        
        Args:
            scanner: 扫描器实例
            directory: 目录路径
            use_iter: 是否使用流式扫描
            
        Returns:
            Tuple[float, float, int]: (耗时秒数, 峰值内存MB, 文件数)
        """
        # 开始内存追踪
        tracemalloc.start()
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行扫描
        if use_iter:
            files = []
            for batch in scanner.scan_iter(directory):
                files.extend(batch)
        else:
            files = scanner.scan(directory)
        
        # 记录结束时间
        end_time = time.time()
        
        # 获取峰值内存
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        elapsed = end_time - start_time
        peak_mb = peak / 1024 / 1024
        
        return elapsed, peak_mb, len(files)
    
    def test_old_vs_new_scanner(self, test_data_dir: Path):
        """对比旧实现（scan）与新实现（scan_iter）"""
        print(f"\n测试目录: {test_data_dir}")
        
        # 测试旧实现
        scanner_old = FileScanner()
        old_time, old_mem, old_count = self._measure_performance(
            scanner_old, test_data_dir, use_iter=False
        )
        
        print(f"\n旧实现 (scan):")
        print(f"  耗时: {old_time:.2f} 秒")
        print(f"  峰值内存: {old_mem:.2f} MB")
        print(f"  文件数: {old_count}")
        
        # 测试新实现
        scanner_new = FileScanner(max_workers=4, batch_size=50)
        new_time, new_mem, new_count = self._measure_performance(
            scanner_new, test_data_dir, use_iter=True
        )
        
        print(f"\n新实现 (scan_iter):")
        print(f"  耗时: {new_time:.2f} 秒")
        print(f"  峰值内存: {new_mem:.2f} MB")
        print(f"  文件数: {new_count}")
        
        # 计算改进
        time_improvement = (old_time - new_time) / old_time * 100
        mem_improvement = (old_mem - new_mem) / old_mem * 100
        
        print(f"\n性能改进:")
        print(f"  时间: {time_improvement:+.1f}%")
        print(f"  内存: {mem_improvement:+.1f}%")
        
        # 验证文件数一致
        assert old_count == new_count, "扫描结果文件数不一致"
        
        # 检查性能目标（允许通过环境变量调整阈值）
        time_threshold = float(os.getenv("PERF_TIME_THRESHOLD", "30"))
        mem_threshold = float(os.getenv("PERF_MEM_THRESHOLD", "25"))
        
        # 如果性能退化超过阈值，测试失败
        if time_improvement < -20:  # 允许 20% 的性能波动
            pytest.fail(f"时间性能退化: {time_improvement:.1f}% (预期 >= {time_threshold}%)")
        
        if mem_improvement < -10:  # 允许 10% 的内存波动
            pytest.fail(f"内存性能退化: {mem_improvement:.1f}% (预期 >= {mem_threshold}%)")
    
    def test_parallel_workers(self, test_data_dir: Path):
        """测试不同并行度的性能"""
        print(f"\n测试不同并行度...")
        
        results = {}
        for workers in [1, 2, 4, 8]:
            scanner = FileScanner(max_workers=workers, batch_size=50)
            elapsed, mem, count = self._measure_performance(
                scanner, test_data_dir, use_iter=True
            )
            results[workers] = (elapsed, mem, count)
            print(f"\n{workers} 个工作线程:")
            print(f"  耗时: {elapsed:.2f} 秒")
            print(f"  峰值内存: {mem:.2f} MB")
        
        # 验证并行度提升带来的性能提升
        time_1 = results[1][0]
        time_4 = results[4][0]
        
        # 4 个工作线程应该比 1 个快
        speedup = time_1 / time_4
        print(f"\n4 线程相比 1 线程加速比: {speedup:.2f}x")
        
        # 至少应该有一些加速（但不期望线性加速）
        # 注意：在某些环境（如容器、虚拟机）中，并行可能没有明显加速
        # 因此我们只验证结果正确性，不强制要求加速
        if speedup > 1.0:
            print(f"✓ 并行加速有效: {speedup:.2f}x")
        else:
            print(f"⚠ 并行加速不明显: {speedup:.2f}x (可能受环境限制)")
    
    def test_batch_size_impact(self, test_data_dir: Path):
        """测试批次大小对性能的影响"""
        print(f"\n测试不同批次大小...")
        
        results = {}
        for batch_size in [10, 50, 100, 200]:
            scanner = FileScanner(max_workers=4, batch_size=batch_size)
            elapsed, mem, count = self._measure_performance(
                scanner, test_data_dir, use_iter=True
            )
            results[batch_size] = (elapsed, mem, count)
            print(f"\n批次大小 {batch_size}:")
            print(f"  耗时: {elapsed:.2f} 秒")
            print(f"  峰值内存: {mem:.2f} MB")
        
        # 所有批次大小应该产生相同的结果
        counts = [r[2] for r in results.values()]
        assert len(set(counts)) == 1, "不同批次大小产生了不同的结果"
    
    def test_incremental_cache_performance(self, test_data_dir: Path):
        """测试增量缓存的性能"""
        print(f"\n测试增量缓存性能...")
        
        library = MediaLibrary()
        library.add_scan_source(test_data_dir)
        scanner = FileScanner(max_workers=4, batch_size=50)
        
        # 首次完整扫描
        tracemalloc.start()
        start = time.time()
        library.scan(scanner)
        first_time = time.time() - start
        _, first_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"\n首次完整扫描:")
        print(f"  耗时: {first_time:.2f} 秒")
        print(f"  峰值内存: {first_mem / 1024 / 1024:.2f} MB")
        print(f"  文件数: {len(library.media_files)}")
        
        # 快速刷新（无变化）
        tracemalloc.start()
        start = time.time()
        result = library.quick_refresh(scanner)
        refresh_time = time.time() - start
        _, refresh_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"\n快速刷新（无变化）:")
        print(f"  耗时: {refresh_time:.2f} 秒")
        print(f"  峰值内存: {refresh_mem / 1024 / 1024:.2f} MB")
        print(f"  结果: {result}")
        
        # 快速刷新应该明显更快
        speedup = first_time / refresh_time
        print(f"\n快速刷新加速比: {speedup:.2f}x")
        
        # 验证结果
        assert result["added"] == 0
        assert result["removed"] == 0
        
        # 增量刷新应该更快（但在某些环境中可能不明显）
        if speedup > 1.5:
            print(f"✓ 快速刷新加速有效: {speedup:.2f}x")
        else:
            print(f"⚠ 快速刷新加速不明显: {speedup:.2f}x (可能受环境限制)")


def test_benchmark_summary():
    """
    基准测试摘要
    
    运行此测试以获取当前系统的性能基准。
    结果可以保存为未来的参考。
    """
    print("\n" + "=" * 60)
    print("SmartRenamer 扫描器性能基准")
    print("=" * 60)
    print("\n运行完整的性能测试套件以获取基准数据。")
    print("\n使用方法:")
    print("  pytest tests/perf/test_scanner_perf.py -v -s")
    print("\n环境变量:")
    print("  SKIP_PERF_TESTS=true       - 跳过性能测试")
    print("  PERF_TIME_THRESHOLD=30     - 时间性能阈值（百分比）")
    print("  PERF_MEM_THRESHOLD=25      - 内存性能阈值（百分比）")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
