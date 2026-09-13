FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# El cierre con hash fija el árbol completo de dependencias y su huella;
# --only-binary impide que pip ejecute el `setup.py` de un paquete al
# instalarlo, que es por donde entra una dependencia comprometida.
COPY requirements.lock.txt .
RUN pip install --no-cache-dir --require-hashes --only-binary :all: \
        -r requirements.lock.txt

COPY app ./app
COPY scripts ./scripts

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
