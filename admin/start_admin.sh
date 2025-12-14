#!/bin/bash
# Start-Script für Admin Server

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
ADMIN_DIR="$PROJECT_ROOT/admin"

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
    log_info "Erstelle mlx_env..."
    cd "$PROJECT_ROOT"
    python3 -m venv mlx_env
fi

# Aktiviere Environment
source "$MLX_ENV/bin/activate"

# Installiere Dependencies falls nötig
log_info "Prüfe Dependencies..."
pip install -q flask flask-cors psutil || {
    log_warn "Einige Dependencies fehlen, installiere..."
    pip install flask flask-cors psutil
}

# Starte Admin Server
log_info "Starte Admin Server..."
log_info "Dashboard: http://localhost:8080"

cd "$ADMIN_DIR"
python3 admin_server.py
