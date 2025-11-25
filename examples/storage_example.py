#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存储适配器使用示例

演示如何使用 SmartRenamer 的存储适配器功能
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

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from smartrenamer.storage import (
    StorageManager,
    LocalStorageAdapter,
    Storage115Adapter,
    Storage123Adapter,
    get_storage_manager
)


def 示例1_本地存储():
    """示例 1：使用本地存储适配器"""
    print("=" * 60)
    print("示例 1：使用本地存储适配器")
    print("=" * 60)
    
    # 创建本地适配器
    适配器 = LocalStorageAdapter()
    
    # 连接
    if 适配器.连接():
        print("✓ 本地存储已连接")
        
        # 获取存储空间信息
        空间信息 = 适配器.获取存储空间信息()
        print(f"\n存储空间信息:")
        print(f"  总空间: {空间信息['总空间'] / (1024**3):.2f} GB")
        print(f"  已用空间: {空间信息['已用空间'] / (1024**3):.2f} GB")
        print(f"  剩余空间: {空间信息['剩余空间'] / (1024**3):.2f} GB")
        print(f"  使用率: {空间信息['使用率']:.2f}%")
        
        # 列出当前目录的文件
        当前目录 = Path.cwd()
        print(f"\n列出当前目录文件: {当前目录}")
        文件列表 = 适配器.列出文件(str(当前目录))
        
        for 文件 in 文件列表[:5]:  # 只显示前 5 个
            文件类型 = "目录" if 文件.是否目录 else "文件"
            print(f"  [{文件类型}] {文件.名称} ({文件.大小} 字节)")
        
        if len(文件列表) > 5:
            print(f"  ... 还有 {len(文件列表) - 5} 个文件/目录")
        
        # 断开连接
        适配器.断开连接()
        print("\n✓ 本地存储已断开")


def 示例2_存储管理器():
    """示例 2：使用存储管理器"""
    print("\n" + "=" * 60)
    print("示例 2：使用存储管理器")
    print("=" * 60)
    
    # 获取全局存储管理器
    管理器 = get_storage_manager()
    
    # 列出可用的存储类型
    可用类型 = 管理器.列出可用适配器()
    print(f"\n可用的存储类型: {', '.join(可用类型)}")
    
    # 切换到本地存储
    if 管理器.切换适配器("local", {}):
        print(f"✓ 已切换到: {管理器.获取当前类型()}")
        
        # 获取当前适配器
        适配器 = 管理器.获取当前适配器()
        if 适配器:
            print(f"  当前适配器类型: {适配器.获取类型().value}")
    
    # 关闭所有适配器
    管理器.关闭所有适配器()
    print("\n✓ 所有适配器已关闭")


def 示例3_过滤和递归():
    """示例 3：使用过滤器和递归扫描"""
    print("\n" + "=" * 60)
    print("示例 3：过滤器和递归扫描")
    print("=" * 60)
    
    # 创建适配器
    适配器 = LocalStorageAdapter()
    适配器.连接()
    
    # 定义过滤器：只列出 Python 文件
    def 是Python文件(文件):
        return 文件.名称.endswith('.py') and not 文件.是否目录
    
    # 扫描示例目录
    示例目录 = Path(__file__).parent
    print(f"\n扫描目录: {示例目录}")
    print("过滤条件: 只显示 .py 文件")
    
    文件列表 = 适配器.列出文件(
        str(示例目录),
        递归=False,
        过滤器=是Python文件
    )
    
    print(f"\n找到 {len(文件列表)} 个 Python 文件:")
    for 文件 in 文件列表:
        print(f"  {文件.名称} ({文件.大小} 字节)")
    
    适配器.断开连接()


def 示例4_流式扫描():
    """示例 4：流式扫描大目录"""
    print("\n" + "=" * 60)
    print("示例 4：流式扫描")
    print("=" * 60)
    
    # 创建适配器
    适配器 = LocalStorageAdapter()
    适配器.连接()
    
    # 流式扫描当前目录
    当前目录 = Path.cwd()
    print(f"\n流式扫描目录: {当前目录}")
    print("批次大小: 10")
    
    批次计数 = 0
    总文件数 = 0
    
    for 批次文件 in 适配器.列出文件迭代(
        str(当前目录),
        递归=False,
        批次大小=10
    ):
        批次计数 += 1
        总文件数 += len(批次文件)
        print(f"\n批次 {批次计数}: {len(批次文件)} 个文件")
        
        # 只显示每批的前 3 个
        for 文件 in 批次文件[:3]:
            文件类型 = "目录" if 文件.是否目录 else "文件"
            print(f"  [{文件类型}] {文件.名称}")
        
        if len(批次文件) > 3:
            print(f"  ... 还有 {len(批次文件) - 3} 个文件")
    
    print(f"\n总计: {批次计数} 个批次, {总文件数} 个文件")
    
    适配器.断开连接()


def 示例5_115网盘_模拟():
    """示例 5：115 网盘适配器（模拟）"""
    print("\n" + "=" * 60)
    print("示例 5：115 网盘适配器（模拟）")
    print("=" * 60)
    
    # 注意：这里只是创建适配器，不会真正连接
    # 实际使用需要提供有效的 cookie
    
    配置 = {
        "cookie": "your_115_cookie_here",
        "user_id": ""
    }
    
    适配器 = Storage115Adapter(配置)
    print(f"✓ 115 网盘适配器已创建")
    print(f"  存储类型: {适配器.获取类型().value}")
    print(f"  Cookie 已配置: {'是' if 配置['cookie'] != 'your_115_cookie_here' else '否'}")
    
    print("\n要使用 115 网盘，请:")
    print("1. 登录 115 网盘 (https://115.com)")
    print("2. 使用浏览器开发者工具获取 Cookie")
    print("3. 更新配置中的 cookie 字段")
    print("4. 调用 适配器.连接() 进行连接")


def 示例6_123网盘_模拟():
    """示例 6：123 网盘适配器（模拟）"""
    print("\n" + "=" * 60)
    print("示例 6：123 网盘适配器（模拟）")
    print("=" * 60)
    
    # 注意：这里只是创建适配器，不会真正连接
    # 实际使用需要提供有效的 token
    
    配置 = {
        "access_token": "your_access_token_here",
        "refresh_token": "your_refresh_token_here"
    }
    
    适配器 = Storage123Adapter(配置)
    print(f"✓ 123 网盘适配器已创建")
    print(f"  存储类型: {适配器.获取类型().value}")
    print(f"  Token 已配置: {'是' if 配置['access_token'] != 'your_access_token_here' else '否'}")
    
    print("\n要使用 123 网盘，请:")
    print("1. 登录 123 网盘 (https://www.123pan.com)")
    print("2. 使用浏览器开发者工具获取 Authorization token")
    print("3. 更新配置中的 access_token 和 refresh_token 字段")
    print("4. 调用 适配器.连接() 进行连接")


def main():
    """运行所有示例"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "SmartRenamer 存储适配器示例" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        # 运行各个示例
        示例1_本地存储()
        示例2_存储管理器()
        示例3_过滤和递归()
        示例4_流式扫描()
        示例5_115网盘_模拟()
        示例6_123网盘_模拟()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
