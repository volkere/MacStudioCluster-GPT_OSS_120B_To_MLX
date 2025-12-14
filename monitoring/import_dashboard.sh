#!/bin/bash
# Import-Script für Grafana Dashboard
# Falls das Dashboard nicht automatisch geladen wird

set -e

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_FILE="$SCRIPT_DIR/grafana/dashboards/cluster-dashboard.json"

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

# Prüfe ob Grafana läuft
if ! curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    log_error "Grafana läuft nicht auf Port 3000"
    log_info "Starte Grafana mit: ./start_grafana.sh"
    exit 1
fi

log_info "Importiere Dashboard in Grafana..."

# Importiere Dashboard über API
# Hinweis: Erfordert Admin-Login
# Standard-Login: admin / admin

# Erstelle temporäre Datei mit korrektem Format
TEMP_FILE=$(mktemp)
cat > "$TEMP_FILE" << 'EOF'
{
  "dashboard": {
    "title": "Mac Studio Cluster Dashboard",
    "tags": ["cluster", "mac-studio", "ray"],
    "timezone": "browser",
    "refresh": "10s",
    "panels": []
  },
  "overwrite": false
}
EOF

# Lade Dashboard-JSON
DASHBOARD_CONTENT=$(cat "$DASHBOARD_FILE")

log_info "Dashboard-Datei gefunden: $DASHBOARD_FILE"
log_info ""
log_info "Manueller Import:"
log_info "1. Öffne http://localhost:3000"
log_info "2. Login mit admin / admin"
log_info "3. Gehe zu: Dashboards → Import"
log_info "4. Lade die Datei: $DASHBOARD_FILE"
log_info ""
log_info "Oder über API (erfordert Authentifizierung):"
log_info "curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \\"
log_info "  -H 'Content-Type: application/json' \\"
log_info "  -d @$DASHBOARD_FILE"

rm -f "$TEMP_FILE"
