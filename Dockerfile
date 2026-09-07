FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home appuser
COPY app ./app
COPY openapi.yaml .
ENV PORT=8000 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER appuser
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port \"${PORT:-8000}\""]
