#!/bin/bash

# Quick Deploy Script - Versão Simples
# Para uso rápido e prático

APP_NAME="monitor-status-app"
CONTAINER_NAME="monitor-status-container"

echo "?? Quick Deploy - Monitor de Status"

# Para container existente
if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
    echo "??  Parando container existente..."
    docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME
fi

# Constrói e executa
echo "?? Construindo imagem..."
docker build -t $APP_NAME:prod . -q

echo "?? Iniciando container em background..."
docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    -p 5000:5000 \
    $APP_NAME:prod

# Verifica se subiu
sleep 3
if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
    echo "? Aplicação rodando em background!"
    echo "?? Acesse: http://localhost:5000"
    echo "?? Ver logs: docker logs $CONTAINER_NAME -f"
    echo "??  Parar: docker stop $CONTAINER_NAME"
else
    echo "? Erro ao iniciar container"
    docker logs $CONTAINER_NAME
fi