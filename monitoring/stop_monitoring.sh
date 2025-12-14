#!/bin/bash
# Stop-Script für alle Monitoring-Services

set -e

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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

log_info "=== Stoppe Monitoring Services ==="

# Stoppe Prometheus
if [ -f "$MONITORING_DIR/.prometheus_pid" ]; then
    PID=$(cat "$MONITORING_DIR/.prometheus_pid")
    if kill -0 "$PID" 2>/dev/null; then
        log_info "Stoppe Prometheus (PID: $PID)..."
        kill "$PID" 2>/dev/null || true
        rm -f "$MONITORING_DIR/.prometheus_pid"
    fi
fi

# Stoppe Grafana
if [ -f "$MONITORING_DIR/.grafana_pid" ]; then
    PID=$(cat "$MONITORING_DIR/.grafana_pid")
    if kill -0 "$PID" 2>/dev/null; then
        log_info "Stoppe Grafana (PID: $PID)..."
        kill "$PID" 2>/dev/null || true
        rm -f "$MONITORING_DIR/.grafana_pid"
    fi
fi

# Stoppe Metrics Collector
if [ -f "$MONITORING_DIR/.metrics_collector_pid" ]; then
    PID=$(cat "$MONITORING_DIR/.metrics_collector_pid")
    if kill -0 "$PID" 2>/dev/null; then
        log_info "Stoppe Metrics Collector (PID: $PID)..."
        kill "$PID" 2>/dev/null || true
        rm -f "$MONITORING_DIR/.metrics_collector_pid"
    fi
fi

# Stoppe auch über Ports
for port in 9090 3000 9091; do
    PIDS=$(lsof -ti :$port 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        log_info "Beende Prozesse auf Port $port..."
        kill -9 $PIDS 2>/dev/null || true
    fi
done

log_info "=== Alle Monitoring Services gestoppt ==="
