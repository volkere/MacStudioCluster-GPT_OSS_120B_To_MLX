#!/bin/bash
# Start-Script für Ray Cluster auf Mac Studio

set -e

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MLX_ENV="$PROJECT_ROOT/mlx_env"
RAY_CONFIG="$SCRIPT_DIR/config.yaml"

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

# Prüfe ob Ray installiert ist
check_ray() {
    if ! command -v ray &> /dev/null; then
        log_error "Ray ist nicht installiert"
        log_info "Installiere Ray..."
        source "$MLX_ENV/bin/activate"
        pip install ray[default]
    fi
}

# Starte Ray Head Node
start_head() {
    log_info "Starte Ray Head Node..."
    
    source "$MLX_ENV/bin/activate"
    
    cd "$PROJECT_ROOT"
    
    # Ray Head starten
    # Port-Konfiguration: GCS auf 6380 (um Konflikte zu vermeiden), Client Server auf 10001, Dashboard auf 8265
    # object_store_memory wird automatisch von Ray gewählt
    ray start --head \
        --port=6380 \
        --ray-client-server-port=10001 \
        --dashboard-host=0.0.0.0 \
        --dashboard-port=8265 \
        --num-cpus=16 \
        --num-gpus=1 \
        --disable-usage-stats
    
    log_info "Ray Head Node gestartet"
    log_info "Dashboard: http://localhost:8265"
}

# Starte Ray Worker Node
start_worker() {
    local head_address=$1
    
    if [ -z "$head_address" ]; then
        log_error "Head Node Adresse erforderlich (z.B. 10.10.10.11:10001)"
        exit 1
    fi
    
    log_info "Starte Ray Worker Node (verbindet zu $head_address)..."
    
    source "$MLX_ENV/bin/activate"
    
    cd "$PROJECT_ROOT"
    
    # Ray Worker starten
    # Worker verwendet automatisch verfügbare Ports
    ray start --address="$head_address" \
        --num-cpus=16 \
        --num-gpus=1 \
        --disable-usage-stats
    
    log_info "Ray Worker Node gestartet"
}

# Hauptfunktion
main() {
    local mode=$1
    local head_address=$2
    
    log_info "=== Ray Cluster Setup ==="
    
    # Prüfe mlx_env
    if [ ! -d "$MLX_ENV" ]; then
        log_error "mlx_env nicht gefunden: $MLX_ENV"
        exit 1
    fi
    
    # Prüfe Ray
    check_ray
    
    case "$mode" in
        head)
            start_head
            ;;
        worker)
            if [ -z "$head_address" ]; then
                log_error "Head Node Adresse erforderlich für Worker Mode"
                log_info "Verwendung: $0 worker <head-ip>:10001"
                exit 1
            fi
            start_worker "$head_address"
            ;;
        *)
            log_error "Unbekannter Modus: $mode"
            log_info "Verwendung:"
            log_info "  $0 head              # Starte Head Node"
            log_info "  $0 worker <head-ip>   # Starte Worker Node"
            exit 1
            ;;
    esac
    
    log_info ""
    log_info "=== Ray Cluster Status ==="
    log_info "Prüfe Status mit: ray status"
    log_info "Dashboard: http://localhost:8265"
}

main "$@"
