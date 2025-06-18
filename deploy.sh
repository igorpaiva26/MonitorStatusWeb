#!/bin/bash

# Script de Deploy do Monitor de Status
# Autor: DevOps Team
# Versão: 1.0

set -e  # Para em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
APP_NAME="monitor-status-app"
IMAGE_TAG="prod"
CONTAINER_NAME="monitor-status-container"
PORT="5000"

# Função para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Função para verificar se o Docker está rodando
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker não está rodando. Inicie o Docker primeiro."
        exit 1
    fi
    log "Docker está rodando"
}

# Função para parar container existente
stop_existing_container() {
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        warn "Container $CONTAINER_NAME já está rodando. Parando..."
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        log "Container anterior removido"
    fi
}

# Função para construir a imagem
build_image() {
    log "Construindo imagem Docker..."
    docker build -t $APP_NAME:$IMAGE_TAG .
    log "Imagem construída com sucesso"
}

# Função para executar o container
run_container() {
    log "Iniciando container em background..."
    docker run -d \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        -p $PORT:$PORT \
        $APP_NAME:$IMAGE_TAG
    
    log "Container iniciado com sucesso"
    info "Nome do container: $CONTAINER_NAME"
    info "Porta: $PORT"
    info "Acesse: http://localhost:$PORT"
}

# Função para verificar se o container está saudável
check_health() {
    log "Verificando saúde da aplicação..."
    sleep 5  # Aguarda inicialização
    
    for i in {1..10}; do
        if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
            log "? Aplicação está saudável!"
            break
        else
            warn "Tentativa $i/10 - Aguardando aplicação ficar disponível..."
            sleep 3
        fi
        
        if [ $i -eq 10 ]; then
            error "? Aplicação não respondeu após 10 tentativas"
            info "Verificando logs do container:"
            docker logs $CONTAINER_NAME --tail 20
            exit 1
        fi
    done
}

# Função para mostrar status
show_status() {
    echo ""
    info "=== STATUS DA APLICAÇÃO ==="
    docker ps -f name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    info "=== COMANDOS ÚTEIS ==="
    echo "Ver logs:           docker logs $CONTAINER_NAME -f"
    echo "Parar aplicação:    docker stop $CONTAINER_NAME"
    echo "Reiniciar:          docker restart $CONTAINER_NAME"
    echo "Entrar no container: docker exec -it $CONTAINER_NAME /bin/bash"
    echo "Remover container:  docker rm -f $CONTAINER_NAME"
    echo ""
}

# Função principal
main() {
    log "?? Iniciando deploy do Monitor de Status"
    
    check_docker
    stop_existing_container
    build_image
    run_container
    check_health
    show_status
    
    log "?? Deploy concluído com sucesso!"
}

# Função para mostrar ajuda
show_help() {
    echo "Monitor Status Deploy Script"
    echo ""
    echo "Uso: ./deploy.sh [OPÇÃO]"
    echo ""
    echo "Opções:"
    echo "  start     Inicia a aplicação (padrão)"
    echo "  stop      Para a aplicação"
    echo "  restart   Reinicia a aplicação"
    echo "  status    Mostra status da aplicação"
    echo "  logs      Mostra logs da aplicação"
    echo "  clean     Remove container e imagem"
    echo "  help      Mostra esta ajuda"
    echo ""
}

# Função para parar aplicação
stop_app() {
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        log "Parando aplicação..."
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        log "Aplicação parada"
    else
        warn "Nenhuma aplicação rodando"
    fi
}

# Função para mostrar logs
show_logs() {
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        info "Mostrando logs (Ctrl+C para sair)..."
        docker logs $CONTAINER_NAME -f
    else
        error "Container não está rodando"
    fi
}

# Função para limpeza
clean_all() {
    log "Limpando containers e imagens..."
    docker rm -f $CONTAINER_NAME 2>/dev/null || true
    docker rmi $APP_NAME:$IMAGE_TAG 2>/dev/null || true
    log "Limpeza concluída"
}

# Parse dos argumentos
case "${1:-start}" in
    start)
        main
        ;;
    stop)
        stop_app
        ;;
    restart)
        stop_app
        main
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    clean)
        clean_all
        ;;
    help)
        show_help
        ;;
    *)
        error "Opção inválida: $1"
        show_help
        exit 1
        ;;
esac