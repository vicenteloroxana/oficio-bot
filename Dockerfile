FROM python:3.12-slim

# WeasyPrint (services/pdf_service.py) necesita las librerías nativas de
# Pango/GObject/Cairo en tiempo de ejecución. Nixpacks no lograba exponer
# estas libs en el runtime (OSError: cannot load library 'libgobject-2.0-0'
# pese a declarar los paquetes Nix correspondientes) — ver docs/adr/001 y
# docs/backlog.md. apt-get instala las mismas libs que pide la guía oficial
# de instalación de WeasyPrint para Debian/Ubuntu.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgobject-2.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
