# Usamos una imagen de Python moderna
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Copiamos los archivos de requisitos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto 5000
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python", "app.py"]
