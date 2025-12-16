#!/bin/bash
# Start-Script für Grafana

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
GRAFANA_DIR="$MONITORING_DIR/grafana"

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

# Prüfe ob Grafana installiert ist
if ! command -v grafana-server &> /dev/null; then
    log_error "Grafana ist nicht installiert"
    log_info "Installiere mit: brew install grafana"
    exit 1
fi

# Prüfe ob Port belegt ist
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    log_warn "Port 3000 ist bereits belegt"
    PID=$(lsof -ti :3000)
    log_info "Beende Prozess $PID..."
    kill $PID 2>/dev/null || true
    sleep 2
fi

# Erstelle Grafana Verzeichnisse
mkdir -p "$GRAFANA_DIR/data"
mkdir -p "$GRAFANA_DIR/logs"

# Starte Grafana
log_info "Starte Grafana..."
log_info "Dashboard: http://localhost:3000"
log_info "Standard-Login: admin / admin"

# Setze Umgebungsvariablen für Grafana
export GF_PATHS_DATA="$GRAFANA_DIR/data"
export GF_PATHS_LOGS="$GRAFANA_DIR/logs"
export GF_PATHS_PROVISIONING="$GRAFANA_DIR/provisioning"
export GF_SERVER_HTTP_PORT=3000
export GF_SERVER_HTTP_ADDRESS=0.0.0.0

grafana-server --homepath=/opt/homebrew/opt/grafana/share/grafana --config=/opt/homebrew/etc/grafana/grafana.ini &

GRAFANA_PID=$!
echo $GRAFANA_PID > "$MONITORING_DIR/.grafana_pid"

log_info "Grafana gestartet (PID: $GRAFANA_PID)"
log_info "Zum Stoppen: ./stop_grafana.sh"


