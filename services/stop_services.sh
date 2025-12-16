#!/bin/bash
# Stop-Script für alle Face Tagging Services

set -e

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$PROJECT_ROOT/services/.service_pids"

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

stop_service() {
    local service_name=$1
    local pid=$2
    
    if [ -z "$pid" ]; then
        log_warn "$service_name: Keine PID gefunden"
        return 1
    fi
    
    if kill -0 "$pid" 2>/dev/null; then
        log_info "Stoppe $service_name (PID: $pid)..."
        kill "$pid"
        
        # Warte auf Beendigung
        local count=0
        while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        if kill -0 "$pid" 2>/dev/null; then
            log_warn "$service_name: Prozess reagiert nicht, erzwinge Beendigung..."
            kill -9 "$pid" 2>/dev/null || true
        fi
        
        log_info "$service_name gestoppt"
        return 0
    else
        log_warn "$service_name: Prozess $pid existiert nicht"
        return 1
    fi
}

stop_by_port() {
    local port=$1
    local service_name=$2
    
    local pids=$(lsof -ti :$port 2>/dev/null || true)
    
    if [ -z "$pids" ]; then
        log_warn "$service_name: Kein Prozess auf Port $port gefunden"
        return 1
    fi
    
    for pid in $pids; do
        log_info "Stoppe Prozess auf Port $port (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
    done
    
    # Warte kurz
    sleep 2
    
    # Erzwinge Beendigung falls nötig
    pids=$(lsof -ti :$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        for pid in $pids; do
            log_warn "Erzwinge Beendigung von Prozess $pid..."
            kill -9 "$pid" 2>/dev/null || true
        done
    fi
    
    log_info "$service_name gestoppt"
}

# Hauptfunktion
main() {
    log_info "=== Face Tagging Services Stop ==="
    
    if [ ! -f "$PID_FILE" ]; then
        log_warn "PID-Datei nicht gefunden: $PID_FILE"
        log_info "Versuche Services über Ports zu stoppen..."
        
        stop_by_port 5001 "Face Detection"
        stop_by_port 5002 "Embedding"
        stop_by_port 8000 "LLM (exo)"
        
        log_info "Fertig"
        return 0
    fi
    
    # Lese PID-Datei
    while IFS=':' read -r service_name pid port; do
        if [ -n "$service_name" ] && [ -n "$pid" ]; then
            stop_service "$service_name" "$pid"
        fi
    done < "$PID_FILE"
    
    # Stoppe auch über Ports (falls PID-Datei unvollständig)
    log_info "Prüfe Ports..."
    stop_by_port 5001 "Face Detection"
    stop_by_port 5002 "Embedding"
    stop_by_port 8000 "LLM (exo)"
    
    # Lösche PID-Datei
    rm -f "$PID_FILE"
    
    log_info ""
    log_info "=== Alle Services gestoppt ==="
}

main "$@"


