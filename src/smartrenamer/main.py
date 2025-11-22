"""
SmartRenamer 主入口文件

启动应用程序
"""
import sys
from pathlib import Path

# 确保可以导入 smartrenamer 包
sys.path.insert(0, str(Path(__file__).parent.parent))

from smartrenamer import __version__
from smartrenamer.core import get_config, Config


def print_banner():
    """打印欢迎横幅"""
    banner = f"""
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║         SmartRenamer v{__version__}           ║
    ║      智能媒体文件重命名工具                  ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)


def main():
    """
    主函数
    
    应用程序的入口点
    """
    print_banner()
    
    # 加载配置
    config = get_config()
    print(f"配置已加载: {config.get_default_config_path()}")
    
    # 验证配置
    is_valid, error_msg = config.validate()
    if not is_valid:
        print(f"⚠️  配置验证失败: {error_msg}")
        print("提示: 请配置 TMDB API Key")
    else:
        print("✓ 配置验证通过")
    
    # TODO: 启动 GUI 界面
    print("\n提示: GUI 界面开发中...")
    print("当前版本仅包含核心架构和数据模型")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
