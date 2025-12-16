#!/bin/bash
# Einfaches Start-Script für einen neuen Node
# Verwendung: ./start-node.sh <node-type> [head-address]

set -e

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Funktionen
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Prüfe Parameter
NODE_TYPE=${1:-worker}
RAY_HEAD=${2:-}

# Korrigiere häufige Tippfehler
case "$NODE_TYPE" in
    mangement|mangment|mangement|managment)
        log_warn "Tippfehler erkannt: '$NODE_TYPE' → 'management'"
        NODE_TYPE=management
        ;;
    workr|worrker|woker)
        log_warn "Tippfehler erkannt: '$NODE_TYPE' → 'worker'"
        NODE_TYPE=worker
        ;;
esac

if [ "$NODE_TYPE" != "worker" ] && [ "$NODE_TYPE" != "management" ]; then
    log_error "Ungültiger Node-Typ: $NODE_TYPE"
    log_info "Verwendung: $0 <worker|management> [head-address]"
    log_info "Hinweis: Häufige Tippfehler werden automatisch korrigiert"
    exit 1
fi

# Prüfe Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker ist nicht installiert"
    log_info "Installiere Docker Desktop für Mac: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Prüfe Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    log_error "Docker Compose ist nicht installiert"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$SCRIPT_DIR"

log_info "=== Starte $NODE_TYPE Node ==="

# Erstelle .env Datei
cat > .env << EOF
NODE_TYPE=$NODE_TYPE
RAY_HEAD_ADDRESS=$RAY_HEAD
RAY_CPUS=16
RAY_GPUS=1
EOF

# Starte Container
if [ "$NODE_TYPE" = "management" ]; then
    log_info "Starte Management Node..."
    docker-compose up -d management
    log_info "Management Node gestartet"
    log_info "Admin Dashboard: http://localhost:8080"
    log_info "Ray Dashboard: http://localhost:8265"
    log_info "Grafana: http://localhost:3000"
elif [ "$NODE_TYPE" = "worker" ]; then
    if [ -z "$RAY_HEAD" ]; then
        log_error "Für Worker Node benötigt: Head Node Adresse"
        log_info "Verwendung: $0 worker <head-ip>:6380"
        log_info "Beispiel: $0 worker 192.168.1.100:6380"
        exit 1
    fi
    
    log_info "Starte Worker Node..."
    log_info "Verbinde zu Head Node: $RAY_HEAD"
    
    # Starte Worker Container
    docker-compose up -d worker1
    
    log_info "Worker Node gestartet"
    log_info "Face Detection: http://localhost:5001"
    log_info "Embedding: http://localhost:5002"
fi

log_info ""
log_info "Container-Status:"
docker-compose ps

log_info ""
log_info "Logs anzeigen: docker-compose logs -f"
log_info "Container stoppen: docker-compose down"


