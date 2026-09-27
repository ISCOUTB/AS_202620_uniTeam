# Imágenes del backend de UniTeam. Dos destinos a partir de la misma base:
#
#   api      la API, que es lo que se despliega. No lleva `scripts/`: una
#            imagen de producción no debe poder firmar tokens de identidad.
#   idp-dev  el emisor OIDC de desarrollo, solo para `docker compose up`.
#
#   docker build --target api -t uniteam-api .
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# El cierre con hash fija el árbol completo de dependencias y su huella;
# --only-binary impide que pip ejecute el `setup.py` de un paquete al
# instalarlo, que es por donde entra una dependencia comprometida.
COPY requirements.lock.txt .
RUN pip install --no-cache-dir --require-hashes --only-binary :all: \
        -r requirements.lock.txt

# Sin privilegios de root en ejecución.
RUN useradd --create-home --uid 10001 uniteam


FROM base AS idp-dev
COPY scripts ./scripts
USER uniteam
CMD ["python", "scripts/emisor_dev.py"]


# El último destino es el predeterminado: `docker build .` produce la API.
FROM base AS api
COPY app ./app
USER uniteam
EXPOSE 8000
# PORT lo fija el proveedor de despliegue; 8000 en local.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
