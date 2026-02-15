FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_SYSTEM_PYTHON=1

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY frontend/app.py ./

EXPOSE 8501
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.address", "0.0.0.0"]