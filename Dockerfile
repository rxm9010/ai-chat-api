# Dockerfile
# 基础镜像走国内镜像站（daocloud 代理 docker hub，内容与官方 python:3.12-slim 一致）
FROM docker.m.daocloud.io/python:3.12-slim

WORKDIR /app

# 安装系统依赖（先把 Debian 软件源切到国内镜像，避免 deb.debian.org 超时/404）
# 兼容两种源格式：新版 deb822（/etc/apt/sources.list.d/debian.sources）与旧版 sources.list
RUN set -eux; \
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true; \
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true; \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件（pip 也走国内镜像）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# 复制项目代码
COPY . .

# 创建非 root 用户（安全最佳实践）
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
