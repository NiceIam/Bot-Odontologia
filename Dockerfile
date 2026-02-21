FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Variable de entorno para el puerto (por defecto 8000)
ENV PORT=8000

# Exponer el puerto dinámicamente
EXPOSE $PORT

# Comando para iniciar la aplicación usando la variable PORT
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
