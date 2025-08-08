FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 创建应用目录
WORKDIR /app

# 先复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装依赖
RUN uv sync --locked

# 复制源代码
COPY . .

# 创建一个入口脚本来处理不同的工作目录
RUN echo '#!/bin/bash\ncd /github/workspace 2>/dev/null || cd /app\nexec uv run main.py "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]