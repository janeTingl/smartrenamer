"""
SmartRenamer 基本使用示例

演示如何使用 SmartRenamer 的核心功能
"""
from pathlib import Path
from smartrenamer import MediaFile, MediaType, Config
from smartrenamer.core import DEFAULT_MOVIE_RULE, DEFAULT_TV_RULE


def example_movie_rename():
    """电影文件重命名示例"""
    print("=" * 60)
    print("示例 1: 电影文件重命名")
    print("=" * 60)
    
    # 创建一个电影文件对象
    movie = MediaFile(
        path=Path("/movies/the.matrix.1999.1080p.bluray.x264.mkv"),
        original_name="the.matrix.1999.1080p.bluray.x264.mkv",
        extension=".mkv",
        media_type=MediaType.MOVIE,
        title="黑客帝国",
        original_title="The Matrix",
        year=1999,
        resolution="1080p",
        source="BluRay",
        codec="x264",
    )
    
    print(f"原文件名: {movie.original_name}")
    print(f"电影标题: {movie.title} ({movie.original_title})")
    print(f"发行年份: {movie.year}")
    print(f"分辨率: {movie.resolution}")
    
    # 应用重命名规则
    new_name = DEFAULT_MOVIE_RULE.apply(movie)
    print(f"\n新文件名: {new_name}")
    print()


def example_tv_show_rename():
    """电视剧文件重命名示例"""
    print("=" * 60)
    print("示例 2: 电视剧文件重命名")
    print("=" * 60)
    
    # 创建一个电视剧文件对象
    tv_episode = MediaFile(
        path=Path("/tvshows/breaking.bad.s01e01.pilot.1080p.mkv"),
        original_name="breaking.bad.s01e01.pilot.1080p.mkv",
        extension=".mkv",
        media_type=MediaType.TV_SHOW,
        title="绝命毒师",
        original_title="Breaking Bad",
        year=2008,
        season_number=1,
        episode_number=1,
        episode_title="Pilot",
        resolution="1080p",
    )
    
    print(f"原文件名: {tv_episode.original_name}")
    print(f"剧集标题: {tv_episode.title} ({tv_episode.original_title})")
    print(f"季/集: S{tv_episode.season_number:02d}E{tv_episode.episode_number:02d}")
    print(f"集标题: {tv_episode.episode_title}")
    
    # 应用重命名规则
    new_name = DEFAULT_TV_RULE.apply(tv_episode)
    print(f"\n新文件名: {new_name}")
    print()


def example_config_management():
    """配置管理示例"""
    print("=" * 60)
    print("示例 3: 配置管理")
    print("=" * 60)
    
    # 创建配置对象
    config = Config(
        tmdb_api_key="your_api_key_here",
        tmdb_language="zh-CN",
        auto_rename=False,
        create_backup=True,
    )
    
    print(f"TMDB 语言: {config.tmdb_language}")
    print(f"自动重命名: {config.auto_rename}")
    print(f"创建备份: {config.create_backup}")
    print(f"支持格式: {', '.join(config.supported_extensions)}")
    
    # 验证配置
    is_valid, error = config.validate()
    print(f"\n配置状态: {'✓ 有效' if is_valid else f'✗ 无效 - {error}'}")
    print()


def example_file_info_extraction():
    """文件信息提取示例"""
    print("=" * 60)
    print("示例 4: 从文件名提取信息")
    print("=" * 60)
    
    from smartrenamer.utils.file_utils import extract_info_from_filename
    
    filenames = [
        "The.Matrix.1999.1080p.BluRay.x264.mkv",
        "Breaking.Bad.S01E05.Gray.Matter.720p.WEB-DL.mkv",
        "Interstellar.2014.2160p.UHD.BluRay.x265.mkv",
    ]
    
    for filename in filenames:
        print(f"\n文件名: {filename}")
        info = extract_info_from_filename(filename)
        print(f"  年份: {info.get('year', 'N/A')}")
        print(f"  分辨率: {info.get('resolution', 'N/A')}")
        print(f"  来源: {info.get('source', 'N/A')}")
        print(f"  编码: {info.get('codec', 'N/A')}")
        if info.get('season') and info.get('episode'):
            print(f"  季集: S{info['season']:02d}E{info['episode']:02d}")
    print()


def main():
    """运行所有示例"""
    print("\n🎬 SmartRenamer 使用示例\n")
    
    example_movie_rename()
    example_tv_show_rename()
    example_config_management()
    example_file_info_extraction()
    
    print("=" * 60)
    print("示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
