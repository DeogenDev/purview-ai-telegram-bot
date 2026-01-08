FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv \
    && uv sync

COPY . /app

ENV BASE_DIR=/app
ENV PYTHONPATH="${PYTHONPATH}:${BASE_DIR}/src:${BASE_DIR}/"

CMD ["uv", "run", "src/main.py"]