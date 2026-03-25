# 使用官方 Python 3.14 镜像（slim 更轻量）
FROM python:3.14-slim

# 环境变量（避免 pyc、stdout 缓冲）
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖（yfinance 可能用到）
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件（利用缓存）
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 再复制项目代码
COPY . .

# 暴露端口
EXPOSE 8001

# 启动命令（生产建议用 uvicorn）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001","--loop", "uvloop", "--http", "httptools"]