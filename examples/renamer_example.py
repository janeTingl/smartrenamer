#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重命名引擎使用示例

演示如何使用 SmartRenamer 的重命名引擎功能
"""

import sys
import os

# 配置标准输出使用 UTF-8 编码，解决 Windows 控制台中文显示问题
if sys.platform == 'win32':
    try:
        # Python 3.7+
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python 3.6 及更早版本
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

from pathlib import Path
from smartrenamer.core import (
    MediaFile,
    MediaType,
    RenameRule,
    Renamer,
    重命名器,
    RenameRuleManager,
    重命名规则管理器,
    create_predefined_rule,
    创建预定义规则,
    PREDEFINED_TEMPLATES,
    预定义模板,
)


def 示例1_查看预定义模板():
    """查看所有预定义模板"""
    print("=" * 60)
    print("示例1: 查看预定义模板")
    print("=" * 60)
    
    print("\n可用的预定义模板:")
    for 模板名称, 模板信息 in 预定义模板.items():
        print(f"\n模板名称: {模板名称}")
        print(f"  描述: {模板信息['描述']}")
        print(f"  模板: {模板信息['模板']}")
        print(f"  示例: {模板信息['示例']}")


def 示例2_使用预定义规则重命名电影():
    """使用预定义规则重命名电影"""
    print("\n" + "=" * 60)
    print("示例2: 使用预定义规则重命名电影")
    print("=" * 60)
    
    # 创建媒体文件对象
    媒体文件 = MediaFile(
        path=Path("/movies/The.Matrix.1999.1080p.BluRay.x264.mkv"),
        original_name="The.Matrix.1999.1080p.BluRay.x264.mkv",
        extension=".mkv",
        media_type=MediaType.MOVIE,
        title="黑客帝国",
        year=1999,
        resolution="1080p",
        source="BluRay",
        codec="H264",
    )
    
    # 使用不同的预定义规则
    模板列表 = ["电影-简洁", "电影-标准", "电影-完整"]
    
    # 创建预览模式的重命名器
    重命名器实例 = 重命名器(预览模式=True)
    
    for 模板名称 in 模板列表:
        规则 = 创建预定义规则(模板名称)
        if 规则:
            成功, 新名称, 错误 = 重命名器实例.生成新文件名(媒体文件, 规则)
            if 成功:
                print(f"\n{模板名称}:")
                print(f"  原文件名: {媒体文件.original_name}")
                print(f"  新文件名: {新名称}")
            else:
                print(f"\n{模板名称}: 生成失败 - {错误}")


def 示例3_使用预定义规则重命名电视剧():
    """使用预定义规则重命名电视剧"""
    print("\n" + "=" * 60)
    print("示例3: 使用预定义规则重命名电视剧")
    print("=" * 60)
    
    # 创建媒体文件对象
    媒体文件 = MediaFile(
        path=Path("/shows/breaking.bad.s01e01.1080p.mkv"),
        original_name="breaking.bad.s01e01.1080p.mkv",
        extension=".mkv",
        media_type=MediaType.TV_SHOW,
        title="绝命毒师",
        year=2008,
        season_number=1,
        episode_number=1,
        episode_title="试播集",
        resolution="1080p",
    )
    
    # 使用不同的预定义规则
    模板列表 = ["电视剧-标准", "电视剧-带剧集名", "电视剧-完整", "电视剧-分季目录"]
    
    # 创建预览模式的重命名器
    重命名器实例 = 重命名器(预览模式=True)
    
    for 模板名称 in 模板列表:
        规则 = 创建预定义规则(模板名称)
        if 规则:
            成功, 新名称, 错误 = 重命名器实例.生成新文件名(媒体文件, 规则)
            if 成功:
                print(f"\n{模板名称}:")
                print(f"  原文件名: {媒体文件.original_name}")
                print(f"  新文件名: {新名称}")
            else:
                print(f"\n{模板名称}: 生成失败 - {错误}")


def 示例4_自定义重命名规则():
    """创建和使用自定义重命名规则"""
    print("\n" + "=" * 60)
    print("示例4: 自定义重命名规则")
    print("=" * 60)
    
    # 创建自定义规则
    自定义规则 = RenameRule(
        name="我的自定义规则",
        description="带分辨率和来源的电影命名",
        template="[{{ year }}] {{ title|清理文件名 }} - {{ resolution|默认值('Unknown') }} - {{ source|默认值('Unknown') }}",
        media_type=MediaType.MOVIE,
    )
    
    媒体文件 = MediaFile(
        path=Path("/movies/movie.mkv"),
        original_name="movie.mkv",
        extension=".mkv",
        media_type=MediaType.MOVIE,
        title="星际穿越",
        year=2014,
        resolution="2160p",
        source="BluRay",
    )
    
    重命名器实例 = 重命名器(预览模式=True)
    成功, 新名称, 错误 = 重命名器实例.生成新文件名(媒体文件, 自定义规则)
    
    if 成功:
        print(f"\n自定义规则: {自定义规则.name}")
        print(f"  模板: {自定义规则.template}")
        print(f"  原文件名: {媒体文件.original_name}")
        print(f"  新文件名: {新名称}")
    else:
        print(f"生成失败: {错误}")


def 示例5_规则管理器():
    """使用规则管理器管理多个规则"""
    print("\n" + "=" * 60)
    print("示例5: 规则管理器")
    print("=" * 60)
    
    # 创建规则管理器
    管理器 = 重命名规则管理器()
    
    # 添加多个规则
    规则1 = RenameRule(
        name="简洁电影规则",
        description="简洁的电影命名",
        template="{{ title }} ({{ year }})",
        media_type=MediaType.MOVIE,
    )
    
    规则2 = RenameRule(
        name="详细电影规则",
        description="详细的电影命名",
        template="{{ title|清理文件名|replace(' ', '.') }}.{{ year }}.{{ resolution }}.{{ source }}",
        media_type=MediaType.MOVIE,
    )
    
    规则3 = RenameRule(
        name="电视剧规则",
        description="电视剧命名",
        template="{{ title }} S{{ season|填充(2) }}E{{ episode|填充(2) }}",
        media_type=MediaType.TV_SHOW,
    )
    
    # 添加规则
    管理器.添加规则(规则1)
    管理器.添加规则(规则2)
    管理器.添加规则(规则3)
    
    print(f"\n已添加 {len(管理器.获取所有规则())} 个规则:")
    for 规则 in 管理器.获取所有规则():
        print(f"  - {规则.name}: {规则.description}")
    
    # 验证模板
    print("\n验证模板:")
    测试模板 = [
        "{{ title }} ({{ year }})",  # 有效
        "{{ title } ({{ year }})",   # 无效 - 语法错误
        "{{ title }} - {{ unknown_var }}",  # 有效 - 变量可以不存在
    ]
    
    for 模板 in 测试模板:
        有效, 错误 = 管理器.验证模板(模板)
        状态 = "✓ 有效" if 有效 else f"✗ 无效: {错误}"
        print(f"  {模板[:30]}... -> {状态}")


def 示例6_批量重命名预览():
    """批量重命名预览"""
    print("\n" + "=" * 60)
    print("示例6: 批量重命名预览")
    print("=" * 60)
    
    # 创建多个媒体文件
    媒体文件列表 = [
        MediaFile(
            path=Path("/movies/movie1.mkv"),
            original_name="movie1.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
            title="盗梦空间",
            year=2010,
            resolution="1080p",
        ),
        MediaFile(
            path=Path("/movies/movie2.mkv"),
            original_name="movie2.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
            title="星际穿越",
            year=2014,
            resolution="2160p",
        ),
        MediaFile(
            path=Path("/movies/movie3.mkv"),
            original_name="movie3.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
            title="致命魔术",
            year=2006,
            resolution="720p",
        ),
    ]
    
    # 创建规则
    规则 = 创建预定义规则("电影-标准")
    
    # 创建预览模式的重命名器
    重命名器实例 = 重命名器(预览模式=True)
    
    # 批量重命名
    结果 = 重命名器实例.批量重命名(媒体文件列表, 规则)
    
    print(f"\n批量重命名结果:")
    print(f"  总数: {结果['总数']}")
    print(f"  成功: {结果['成功']}")
    print(f"  失败: {结果['失败']}")
    print(f"  跳过: {结果['跳过']}")
    
    print("\n详细信息:")
    for 详情 in 结果['详情']:
        if 详情['状态'] == '成功' or 详情['状态'] == 'preview':
            原名 = Path(详情['文件']).name
            新名 = 详情.get('新名称', '未知')
            print(f"  {原名} -> {新名}")


def 示例7_使用自定义过滤器():
    """演示自定义 Jinja2 过滤器的使用"""
    print("\n" + "=" * 60)
    print("示例7: 使用自定义过滤器")
    print("=" * 60)
    
    # 创建带各种过滤器的规则
    规则 = RenameRule(
        name="过滤器演示",
        description="演示各种自定义过滤器",
        template="{{ title|清理文件名|截断(20)|全大写|replace(' ', '_') }}_{{ year }}",
        media_type=MediaType.MOVIE,
    )
    
    媒体文件 = MediaFile(
        path=Path("/test/movie.mkv"),
        original_name="movie.mkv",
        extension=".mkv",
        media_type=MediaType.MOVIE,
        title="这是一个非常非常长的电影标题名称用于测试截断功能",
        year=2024,
    )
    
    重命名器实例 = 重命名器(预览模式=True)
    成功, 新名称, 错误 = 重命名器实例.生成新文件名(媒体文件, 规则)
    
    if 成功:
        print(f"\n原标题: {媒体文件.title}")
        print(f"模板: {规则.template}")
        print(f"结果: {新名称}")
        print("\n应用的过滤器:")
        print("  1. 清理文件名: 移除非法字符")
        print("  2. 截断(20): 限制长度为20字符")
        print("  3. 全大写: 转换为大写")
        print("  4. replace(' ', '_'): 空格替换为下划线")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("SmartRenamer 重命名引擎使用示例")
    print("=" * 60)
    
    try:
        示例1_查看预定义模板()
        示例2_使用预定义规则重命名电影()
        示例3_使用预定义规则重命名电视剧()
        示例4_自定义重命名规则()
        示例5_规则管理器()
        示例6_批量重命名预览()
        示例7_使用自定义过滤器()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
