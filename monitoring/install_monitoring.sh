#!/bin/bash
# Installations-Script für Grafana und Prometheus Monitoring

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

log_info "=== Monitoring Installation ==="

# Prüfe Homebrew
if ! command -v brew &> /dev/null; then
    log_error "Homebrew ist nicht installiert"
    exit 1
fi

# Installiere Grafana
log_info "Installiere Grafana..."
if brew list grafana &> /dev/null; then
    log_warn "Grafana ist bereits installiert"
else
    brew install grafana
    log_info "Grafana installiert"
fi

# Installiere Prometheus
log_info "Installiere Prometheus..."
if brew list prometheus &> /dev/null; then
    log_warn "Prometheus ist bereits installiert"
else
    brew install prometheus
    log_info "Prometheus installiert"
fi

# Erstelle Verzeichnisse
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MONITORING_DIR="$PROJECT_ROOT/monitoring"

mkdir -p "$MONITORING_DIR/prometheus"
mkdir -p "$MONITORING_DIR/grafana/provisioning/datasources"
mkdir -p "$MONITORING_DIR/grafana/provisioning/dashboards"
mkdir -p "$MONITORING_DIR/grafana/dashboards"

log_info "Verzeichnisse erstellt"

# Prometheus Config
log_info "Erstelle Prometheus Konfiguration..."
cat > "$MONITORING_DIR/prometheus/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'cluster-metrics'
    static_configs:
      - targets: ['localhost:9091']
        labels:
          instance: 'mac-studio-cluster'
  
  - job_name: 'ray-cluster'
    static_configs:
      - targets: ['localhost:8265']
        labels:
          instance: 'ray-head'
  
  - job_name: 'services'
    static_configs:
      - targets: 
          - 'localhost:5001'
          - 'localhost:5002'
          - 'localhost:8000'
        labels:
          instance: 'face-tagging-services'
EOF

# Grafana Datasource
log_info "Erstelle Grafana Datasource Konfiguration..."
cat > "$MONITORING_DIR/grafana/provisioning/datasources/prometheus.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
    editable: true
EOF

log_info ""
log_info "=== Installation abgeschlossen ==="
log_info ""
log_info "Nächste Schritte:"
log_info "1. Starte Prometheus: ./monitoring/start_prometheus.sh"
log_info "2. Starte Grafana: ./monitoring/start_grafana.sh"
log_info "3. Starte Metrics Collector: ./monitoring/start_metrics_collector.sh"
log_info ""
log_info "Grafana Dashboard: http://localhost:3000"
log_info "  Standard-Login: admin / admin"
log_info "Prometheus: http://localhost:9090"
