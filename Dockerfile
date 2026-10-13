# Imagen de producción de la API de UniTeam.
#
# El destino api es el predeterminado. idp-dev existe únicamente para el
# compose local y no debe desplegarse en Dokploy.
FROM python:3.11.11-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build
COPY requirements.prod.txt ./

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --only-binary=:all: -r requirements.prod.txt


FROM python:3.11.11-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY app ./app

RUN useradd --create-home --uid 10001 --user-group uniteam


FROM runtime AS idp-dev

# Este destino es solo para el entorno local y nunca debe publicarse.
COPY scripts ./scripts
USER uniteam
EXPOSE 9000
CMD ["python", "scripts/emisor_dev.py"]


FROM runtime AS api

# La migración es un comando explícito del despliegue; el emisor de desarrollo
# no entra en esta imagen.
COPY scripts/migrate.py ./scripts/migrate.py
USER uniteam
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/health', timeout=4)" || exit 1
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
