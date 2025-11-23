# ===================================
# 阶段 1: 构建阶段
# ===================================
FROM python:3.11-slim AS builder

# 设置工作目录
WORKDIR /build

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt setup.py pyproject.toml ./
COPY src ./src

# 安装 Python 依赖到临时目录
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt && \
    pip install --no-cache-dir --prefix=/install -e .

# ===================================
# 阶段 2: 运行阶段
# ===================================
FROM python:3.11-slim

# 设置元数据标签
LABEL maintainer="SmartRenamer Team" \
      version="0.5.0" \
      description="智能媒体文件重命名工具 - Docker 版本"

# 安装运行时依赖
# - libgl1: OpenGL 库（PySide6 需要）
# - libxcb-xinerama0: X11 支持
# - libxcb-cursor0: 鼠标光标支持
# - libxkbcommon-x11-0: 键盘支持
# - libdbus-1-3: D-Bus 消息总线
# - x11-apps: X11 测试工具（可选，用于调试）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libfontconfig1 \
    libxrender1 \
    libxrandr2 \
    libxi6 \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制已安装的 Python 包
COPY --from=builder /install /usr/local

# 创建应用目录
WORKDIR /app

# 复制应用代码
COPY src ./src
COPY setup.py pyproject.toml ./
COPY examples ./examples

# 创建数据目录
RUN mkdir -p /data/media /data/config /data/cache

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/data/config \
    XDG_CONFIG_HOME=/data/config \
    XDG_CACHE_HOME=/data/cache \
    DISPLAY=:0 \
    QT_QPA_PLATFORM=xcb

# 复制入口脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 设置卷挂载点
VOLUME ["/data/media", "/data/config", "/data/cache"]

# 暴露端口（为未来的 Web UI 预留）
# EXPOSE 8080

# 设置入口点和默认命令
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["gui"]
