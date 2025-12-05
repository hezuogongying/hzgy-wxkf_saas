# 多阶段构建Dockerfile
FROM python:3.11-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# 生产阶段
FROM python:3.11-slim as production

# 创建非root用户
RUN groupadd -r wxkf && useradd -r -g wxkf wxkf

# 设置工作目录
WORKDIR /app

# 复制已安装的包
COPY --from=builder /root/.local /home/wxkf/.local

# 复制应用代码
COPY . .

# 设置权限
RUN chown -R wxkf:wxkf /app
USER wxkf

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/wxkf/.local/bin:$PATH

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${FASTAPI_PORT:-8083}/health || exit 1

# 暴露端口
EXPOSE 8083

# 启动命令
CMD ["gunicorn", "main:app", \
     "--bind", "0.0.0.0:8083", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--preload", \
     "--timeout", "120", \
     "--keep-alive", "2", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]