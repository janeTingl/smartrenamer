#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 UTF-8 编码修复

验证脚本在 Windows 上能否正确输出中文
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


def main():
    """主函数"""
    print("=" * 60)
    print("UTF-8 编码测试")
    print("=" * 60)
    
    # 测试基本中文输出
    print("\n测试 1: 基本中文输出")
    print("  中文: 成功！")
    print("  平台: {}".format(sys.platform))
    print("  Python 版本: {}".format(sys.version))
    
    # 测试各种中文字符
    print("\n测试 2: 各种中文字符")
    print("  ✓ 简体中文: 测试成功")
    print("  ✓ 繁体中文: 測試成功")
    print("  ✓ 特殊符号: ➜ ✓ ✗ ⚠ ℹ")
    print("  ✓ Emoji: 🎉 🚀 ✨ 📝")
    
    # 测试标准输出和标准错误
    print("\n测试 3: 标准输出和标准错误")
    print("  标准输出: 这是标准输出的中文")
    sys.stderr.write("  标准错误: 这是标准错误的中文\n")
    
    # 测试编码信息
    print("\n测试 4: 编码信息")
    try:
        print("  stdout 编码: {}".format(sys.stdout.encoding))
        print("  stderr 编码: {}".format(sys.stderr.encoding))
    except Exception as e:
        print("  无法获取编码信息: {}".format(e))
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
