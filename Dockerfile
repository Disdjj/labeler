FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
COPY . .
RUN uv sync --locked

CMD ["uv", "run", "main.py"]