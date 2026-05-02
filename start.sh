#!/bin/bash
echo "🚀 Iniciando IA Server..."

# Abrir el puerto 5000 en el firewall
sudo ufw allow 5000/tcp

# Construir la imagen
docker build -t ia-server .

# Limpiar contenedores previos
docker stop ia-interface 2>/dev/null
docker rm ia-interface 2>/dev/null

# Ejecutar con acceso a la red local para ver a Ollama
docker run -d --network="host" --name ia-interface ia-server

echo "✅ IA Server iniciado y puerto 5000 abierto."
