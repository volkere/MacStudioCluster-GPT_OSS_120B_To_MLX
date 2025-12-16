#!/bin/bash
# Start-Script für Prometheus

set -e

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MONITORING_DIR="$SCRIPT_DIR"
PROMETHEUS_DIR="$MONITORING_DIR/prometheus"

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

# Prüfe ob Prometheus installiert ist
if ! command -v prometheus &> /dev/null; then
    log_error "Prometheus ist nicht installiert"
    log_info "Installiere mit: brew install prometheus"
    exit 1
fi

# Prüfe ob Port belegt ist
if lsof -Pi :9090 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    log_warn "Port 9090 ist bereits belegt"
    PID=$(lsof -ti :9090)
    log_info "Beende Prozess $PID..."
    kill $PID 2>/dev/null || true
    sleep 2
fi

# Starte Prometheus
log_info "Starte Prometheus..."
log_info "Konfiguration: $PROMETHEUS_DIR/prometheus.yml"
log_info "Web-Interface: http://localhost:9090"

cd "$PROMETHEUS_DIR"
prometheus --config.file=prometheus.yml --storage.tsdb.path=./data --web.listen-address=0.0.0.0:9090 &

PROMETHEUS_PID=$!
echo $PROMETHEUS_PID > "$MONITORING_DIR/.prometheus_pid"

log_info "Prometheus gestartet (PID: $PROMETHEUS_PID)"
log_info "Zum Stoppen: ./stop_prometheus.sh"


