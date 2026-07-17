FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    DECISION360_DB=/app/var/decision360.db

WORKDIR /app
COPY pyproject.toml requirements-runtime.txt README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir --requirement requirements-runtime.txt \
    && python -m pip install --no-cache-dir --no-deps . \
    && addgroup --system decision360 \
    && adduser --system --ingroup decision360 decision360 \
    && mkdir -p /app/var \
    && chown -R decision360:decision360 /app/var

USER decision360
EXPOSE 8000
VOLUME ["/app/var"]
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import json,urllib.request; assert json.load(urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2))['status']=='ok'"
CMD ["python", "-m", "decision360.api"]
