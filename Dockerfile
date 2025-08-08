FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 先复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装依赖
RUN uv sync --locked

# 复制源代码
COPY . .

CMD ["uv", "run", "main.py"]