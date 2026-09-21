FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libjpeg62-turbo zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Data (SQLite file + private media) lives on a mounted volume, never in the image.
RUN mkdir -p /data/media_storage && useradd -r -u 1001 salonefix && chown -R salonefix /app /data
USER salonefix

ENV DATABASE_URL=sqlite:////data/salonefix.db \
    STORAGE_DIR=/data/media_storage \
    APP_ENV=staging

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

# Migrations run on startup (app.db.init_db.run_migrations) before the API accepts traffic.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
