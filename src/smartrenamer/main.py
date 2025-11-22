"""
SmartRenamer 主入口文件

启动应用程序
"""
import sys
import logging
from pathlib import Path

# 确保可以导入 smartrenamer 包
sys.path.insert(0, str(Path(__file__).parent.parent))

from smartrenamer import __version__
from smartrenamer.core import get_config


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


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
    
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 加载配置
    config = get_config()
    logger.info(f"配置已加载: {config.get_default_config_path()}")
    
    # 启动 GUI 界面
    try:
        from PySide6.QtWidgets import QApplication
        from smartrenamer.ui import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("SmartRenamer")
        app.setApplicationVersion(__version__)
        
        # 创建并显示主窗口
        window = MainWindow()
        window.show()
        
        logger.info("GUI 界面已启动")
        
        return app.exec()
        
    except ImportError as e:
        logger.error(f"无法启动 GUI 界面: {e}")
        print("\n错误: 无法导入 PySide6")
        print("请安装依赖: pip install PySide6")
        return 1
    except Exception as e:
        logger.error(f"启动失败: {e}", exc_info=True)
        print(f"\n错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
