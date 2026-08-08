FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY backend/pyproject.toml ./backend/pyproject.toml
COPY sdk ./sdk
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ./sdk ./backend

COPY backend/app ./backend/app

WORKDIR /app/backend
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
