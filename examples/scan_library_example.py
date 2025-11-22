"""
媒体库扫描示例

演示如何使用 FileScanner 和 MediaLibrary 扫描和管理媒体文件
"""
from pathlib import Path
from smartrenamer import FileScanner, MediaLibrary, MediaType


def 基本扫描示例():
    """基本的目录扫描示例"""
    print("=" * 60)
    print("基本扫描示例")
    print("=" * 60)
    
    # 创建文件扫描器
    scanner = FileScanner(
        min_file_size=1 * 1024 * 1024,  # 最小 1 MB
        max_depth=5  # 最大深度 5 层
    )
    
    # 扫描目录（请替换为实际目录路径）
    scan_path = Path("/path/to/your/media/folder")
    
    if scan_path.exists():
        print(f"\n正在扫描: {scan_path}")
        media_files = scanner.scan(scan_path)
        
        # 显示结果
        print(f"\n找到 {len(media_files)} 个媒体文件:")
        for mf in media_files[:5]:  # 只显示前 5 个
            print(f"  - {mf.title} ({mf.media_type.value})")
        
        # 显示统计信息
        stats = scanner.get_statistics()
        print(f"\n统计信息:")
        print(f"  扫描文件总数: {stats['扫描文件总数']}")
        print(f"  找到媒体文件数: {stats['找到媒体文件数']}")
        print(f"  跳过文件数: {stats['跳过文件数']}")
    else:
        print(f"\n错误: 目录不存在: {scan_path}")
        print("请修改脚本中的 scan_path 为实际的媒体目录路径")


def 媒体库管理示例():
    """媒体库管理示例"""
    print("\n" + "=" * 60)
    print("媒体库管理示例")
    print("=" * 60)
    
    # 创建媒体库
    library = MediaLibrary(enable_cache=True)
    
    # 添加扫描源
    source1 = Path("/path/to/movies")
    source2 = Path("/path/to/tv_shows")
    
    # 检查目录是否存在
    existing_sources = [s for s in [source1, source2] if s.exists()]
    
    if not existing_sources:
        print("\n错误: 没有找到有效的扫描源目录")
        print("请修改脚本中的 source1 和 source2 为实际的目录路径")
        return
    
    for source in existing_sources:
        library.add_scan_source(source)
        print(f"\n添加扫描源: {source}")
    
    # 扫描媒体库
    print("\n正在扫描媒体库...")
    scanner = FileScanner(min_file_size=1 * 1024 * 1024)
    total = library.scan(scanner)
    
    print(f"\n扫描完成! 找到 {total} 个媒体文件")
    
    # 显示统计信息
    stats = library.get_statistics()
    print(f"\n媒体库统计:")
    print(f"  总文件数: {stats['总文件数']}")
    print(f"  电影数: {stats['电影数']}")
    print(f"  电视剧数: {stats['电视剧数']}")
    print(f"  未知类型数: {stats['未知类型数']}")
    
    # 查询示例
    movies = library.get_movies()
    if movies:
        print(f"\n电影列表 (前 5 个):")
        for movie in movies[:5]:
            print(f"  - {movie.title} ({movie.year})")
    
    tv_shows = library.get_tv_shows()
    if tv_shows:
        print(f"\n电视剧列表 (前 5 个):")
        for tv_show in tv_shows[:5]:
            season_ep = f"S{tv_show.season_number:02d}E{tv_show.episode_number:02d}"
            print(f"  - {tv_show.title} - {season_ep}")


def 搜索示例():
    """搜索媒体文件示例"""
    print("\n" + "=" * 60)
    print("搜索示例")
    print("=" * 60)
    
    # 创建并扫描媒体库
    library = MediaLibrary(enable_cache=True)
    scan_path = Path("/path/to/media")
    
    if not scan_path.exists():
        print(f"\n错误: 目录不存在: {scan_path}")
        return
    
    library.add_scan_source(scan_path)
    scanner = FileScanner(min_file_size=1 * 1024 * 1024)
    library.scan(scanner)
    
    # 按标题搜索
    search_title = "Matrix"  # 修改为你想搜索的标题
    results = library.search_by_title(search_title)
    
    if results:
        print(f"\n搜索 '{search_title}' 的结果:")
        for result in results:
            print(f"  - {result.title} ({result.year})")
            print(f"    路径: {result.path}")
            print(f"    大小: {result.size / (1024**3):.2f} GB")
    else:
        print(f"\n未找到匹配 '{search_title}' 的媒体文件")


def 缓存示例():
    """缓存使用示例"""
    print("\n" + "=" * 60)
    print("缓存示例")
    print("=" * 60)
    
    # 创建媒体库并启用缓存
    library = MediaLibrary(enable_cache=True)
    
    # 尝试加载缓存
    print("\n尝试加载缓存...")
    if library.load_cache():
        print("缓存加载成功!")
        stats = library.get_statistics()
        print(f"从缓存加载了 {stats['总文件数']} 个媒体文件")
    else:
        print("没有找到缓存，需要重新扫描")
        
        # 扫描并保存缓存
        scan_path = Path("/path/to/media")
        if scan_path.exists():
            library.add_scan_source(scan_path)
            scanner = FileScanner(min_file_size=1 * 1024 * 1024)
            library.scan(scanner)  # scan() 会自动保存缓存
            print("扫描完成并已保存到缓存")


def 增量更新示例():
    """增量更新示例"""
    print("\n" + "=" * 60)
    print("增量更新示例")
    print("=" * 60)
    
    # 创建媒体库
    library = MediaLibrary(enable_cache=True)
    
    # 加载缓存或执行首次扫描
    if library.load_cache():
        print("从缓存加载媒体库")
    else:
        print("执行首次扫描...")
        scan_path = Path("/path/to/media")
        if not scan_path.exists():
            print(f"错误: 目录不存在: {scan_path}")
            return
        
        library.add_scan_source(scan_path)
        scanner = FileScanner(min_file_size=1 * 1024 * 1024)
        library.scan(scanner)
    
    # 执行增量更新
    print("\n执行增量更新...")
    scanner = FileScanner(min_file_size=1 * 1024 * 1024)
    result = library.update(scanner)
    
    print(f"\n更新结果:")
    print(f"  新增文件: {result['added']}")
    print(f"  删除文件: {result['removed']}")


def 进度回调示例():
    """带进度回调的扫描示例"""
    print("\n" + "=" * 60)
    print("进度回调示例")
    print("=" * 60)
    
    def progress_callback(current_file, scanned, found):
        """进度回调函数"""
        if scanned % 100 == 0:  # 每 100 个文件打印一次
            print(f"已扫描: {scanned} 个文件, 找到: {found} 个媒体文件")
    
    scanner = FileScanner(min_file_size=1 * 1024 * 1024)
    scan_path = Path("/path/to/media")
    
    if scan_path.exists():
        print(f"\n开始扫描: {scan_path}")
        media_files = scanner.scan(scan_path, progress_callback=progress_callback)
        print(f"\n扫描完成! 总共找到 {len(media_files)} 个媒体文件")
    else:
        print(f"错误: 目录不存在: {scan_path}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "SmartRenamer 媒体库扫描示例" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # 运行示例（根据需要注释/取消注释）
    print("\n注意: 请先修改示例代码中的目录路径为实际的媒体目录路径\n")
    
    # 基本扫描示例()
    # 媒体库管理示例()
    # 搜索示例()
    # 缓存示例()
    # 增量更新示例()
    # 进度回调示例()
    
    print("\n")
    print("提示: 取消注释上面的函数调用来运行相应的示例")
    print("\n")
