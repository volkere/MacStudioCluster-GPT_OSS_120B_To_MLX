#!/bin/bash
# Stop-Script für Ray Cluster

set -e

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

# Stoppe Ray
stop_ray() {
    log_info "Stoppe Ray Cluster..."
    
    if command -v ray &> /dev/null; then
        ray stop --force || true
        log_info "Ray Cluster gestoppt"
    else
        log_warn "Ray nicht gefunden, versuche Prozesse zu beenden..."
        
        # Finde Ray-Prozesse
        pids=$(pgrep -f "ray" || true)
        if [ -n "$pids" ]; then
            log_info "Beende Ray-Prozesse..."
            kill -9 $pids 2>/dev/null || true
        fi
    fi
    
    # Prüfe Ports
    log_info "Prüfe Ports..."
    
    for port in 10001 8265 10002; do
        pids=$(lsof -ti :$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            log_info "Beende Prozesse auf Port $port..."
            kill -9 $pids 2>/dev/null || true
        fi
    done
    
    log_info "Ray Cluster vollständig gestoppt"
}

# Hauptfunktion
main() {
    log_info "=== Ray Cluster Stop ==="
    stop_ray
}

main "$@"
