#!/bin/bash
# Start-Script für Metrics Collector

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
MONITORING_DIR="$SCRIPT_DIR"

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

# Prüfe mlx_env
if [ ! -d "$MLX_ENV" ]; then
    log_error "mlx_env nicht gefunden: $MLX_ENV"
    exit 1
fi

# Aktiviere Environment
source "$MLX_ENV/bin/activate"

# Prüfe ob Port belegt ist
if lsof -Pi :9091 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    log_warn "Port 9091 ist bereits belegt"
    PID=$(lsof -ti :9091)
    log_info "Beende Prozess $PID..."
    kill $PID 2>/dev/null || true
    sleep 2
fi

# Starte Metrics Collector
log_info "Starte Metrics Collector..."
log_info "Metrics Endpoint: http://localhost:9091/metrics"

cd "$MONITORING_DIR"
nohup python3 metrics_collector.py > metrics_collector.log 2>&1 &

COLLECTOR_PID=$!
echo $COLLECTOR_PID > "$MONITORING_DIR/.metrics_collector_pid"

log_info "Metrics Collector gestartet (PID: $COLLECTOR_PID)"
log_info "Log: $MONITORING_DIR/metrics_collector.log"
log_info "Zum Stoppen: ./stop_metrics_collector.sh"


