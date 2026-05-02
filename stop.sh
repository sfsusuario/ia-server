#!/bin/bash
echo "🛑 Deteniendo IA Server..."

# Cerrar el puerto 5000 por seguridad
sudo ufw deny 5000/tcp

# Detener y eliminar contenedor
docker stop ia-interface
docker rm ia-interface

echo "✅ Servidor detenido y puerto 5000 cerrado."
