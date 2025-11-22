"""
文件名解析和 TMDB 匹配示例

展示如何使用文件名解析器和智能匹配器
"""
from pathlib import Path
from smartrenamer.core import FileNameParser, Matcher, MediaFile
from smartrenamer.api import EnhancedTMDBClient


def 演示解析器():
    """演示文件名解析器的使用"""
    print("=" * 60)
    print("文件名解析器示例")
    print("=" * 60)
    
    解析器 = FileNameParser()
    
    # 测试文件名列表
    测试文件 = [
        "The.Matrix.1999.1080p.BluRay.x264.mkv",
        "Breaking.Bad.S01E01.Pilot.1080p.WEB-DL.mkv",
        "让子弹飞.2010.4K.BluRay.H265.mkv",
        "权力的游戏.S08E06.1080p.WEB-DL.mkv",
    ]
    
    for 文件名 in 测试文件:
        print(f"\n文件名: {文件名}")
        结果 = 解析器.parse(文件名)
        
        print(f"  类型: {结果['media_type'].value}")
        print(f"  标题: {结果['title']}")
        if 结果['year']:
            print(f"  年份: {结果['year']}")
        if 结果['season'] and 结果['episode']:
            print(f"  季集: S{结果['season']:02d}E{结果['episode']:02d}")
        if 结果['resolution']:
            print(f"  分辨率: {结果['resolution']}")
        if 结果['source']:
            print(f"  来源: {结果['source']}")
        if 结果['codec']:
            print(f"  编码: {结果['codec']}")


def 演示匹配器(api_key: str):
    """
    演示智能匹配器的使用
    
    Args:
        api_key: TMDB API 密钥
    """
    print("\n\n" + "=" * 60)
    print("智能匹配器示例")
    print("=" * 60)
    
    # 创建 TMDB 客户端
    客户端 = EnhancedTMDBClient(api_key, 启用缓存=True)
    
    # 创建匹配器
    匹配器 = Matcher(客户端)
    
    # 测试文件
    测试文件 = [
        "The.Matrix.1999.1080p.BluRay.mkv",
        "Breaking.Bad.S01E01.1080p.mkv",
    ]
    
    for 文件名 in 测试文件:
        print(f"\n正在匹配: {文件名}")
        
        try:
            匹配列表 = 匹配器.match_file(文件名, max_results=3)
            
            if 匹配列表:
                print(f"找到 {len(匹配列表)} 个匹配结果:")
                for i, 匹配 in enumerate(匹配列表, 1):
                    tmdb数据 = 匹配.tmdb数据
                    标题 = tmdb数据.get('title') or tmdb数据.get('name', 'Unknown')
                    年份 = ""
                    if tmdb数据.get('release_date'):
                        年份 = f" ({tmdb数据['release_date'][:4]})"
                    elif tmdb数据.get('first_air_date'):
                        年份 = f" ({tmdb数据['first_air_date'][:4]})"
                    
                    print(f"  {i}. {标题}{年份}")
                    print(f"     相似度: {匹配.相似度:.2%}")
                    print(f"     原因: {匹配.匹配原因}")
            else:
                print("  未找到匹配结果")
                
        except Exception as e:
            print(f"  匹配失败: {e}")


def 演示完整流程(api_key: str):
    """
    演示完整的解析、匹配和应用流程
    
    Args:
        api_key: TMDB API 密钥
    """
    print("\n\n" + "=" * 60)
    print("完整流程示例")
    print("=" * 60)
    
    # 创建组件
    客户端 = EnhancedTMDBClient(api_key, 启用缓存=True)
    匹配器 = Matcher(客户端)
    
    # 创建一个媒体文件对象
    文件路径 = Path("/media/movies/Inception.2010.1080p.BluRay.mkv")
    媒体文件 = MediaFile(
        path=文件路径,
        original_name=文件路径.name,
        extension=".mkv"
    )
    
    print(f"\n原始文件: {媒体文件.original_name}")
    
    try:
        # 执行匹配
        匹配列表 = 匹配器.match_media_file(媒体文件, max_results=1)
        
        if 匹配列表:
            最佳匹配 = 匹配列表[0]
            print(f"\n找到最佳匹配:")
            tmdb数据 = 最佳匹配.tmdb数据
            print(f"  标题: {tmdb数据.get('title', 'Unknown')}")
            print(f"  TMDB ID: {tmdb数据.get('id')}")
            print(f"  相似度: {最佳匹配.相似度:.2%}")
            
            # 应用匹配到媒体文件
            更新后文件 = 匹配器.apply_match_to_media_file(媒体文件, 最佳匹配)
            
            print(f"\n更新后的媒体文件信息:")
            print(f"  标题: {更新后文件.title}")
            print(f"  年份: {更新后文件.year}")
            print(f"  TMDB ID: {更新后文件.tmdb_id}")
            print(f"  类型: {更新后文件.media_type.value}")
        else:
            print("\n未找到匹配结果")
            
    except Exception as e:
        print(f"\n处理失败: {e}")


def main():
    """主函数"""
    # 演示解析器（不需要 API key）
    演示解析器()
    
    # 如果有 TMDB API key，可以演示匹配器
    # 从环境变量或配置文件读取 API key
    import os
    api_key = os.environ.get("TMDB_API_KEY")
    
    if api_key:
        演示匹配器(api_key)
        演示完整流程(api_key)
    else:
        print("\n\n" + "=" * 60)
        print("提示: 设置 TMDB_API_KEY 环境变量以运行匹配器示例")
        print("=" * 60)


if __name__ == "__main__":
    main()
