# Usa la versión más reciente de Python 3.12
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia primero los requisitos para aprovechar la cache
COPY requirements.txt .

# Instala dependencias sin caché
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación
COPY . .

# Expone el puerto (Flask usa el 5000 por defecto)
EXPOSE 8000

# Comando por defecto para correr la app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]