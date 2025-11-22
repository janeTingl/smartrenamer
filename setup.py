"""
SmartRenamer 安装配置文件
"""
from setuptools import setup, find_packages

setup(
    name="smartrenamer",
    version="0.1.0",
    description="智能媒体文件重命名工具",
    author="SmartRenamer Team",
    python_requires=">=3.8",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests>=2.31.0",
        "tmdbv3api>=1.9.0",
        "PySide6>=6.6.0",
        "Jinja2>=3.1.2",
        "Pillow>=10.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "smartrenamer=smartrenamer.main:main",
        ],
    },
)
