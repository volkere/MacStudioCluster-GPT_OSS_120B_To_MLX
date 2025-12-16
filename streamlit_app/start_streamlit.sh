#!/bin/bash
# Start-Script für Streamlit App

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
STREAMLIT_APP="$SCRIPT_DIR/app.py"

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

# Prüfe Python-Environment
PYTHON_PATH=$(which python)
log_info "Verwende Python: $PYTHON_PATH"

# Installiere Dependencies falls nötig
log_info "Prüfe Dependencies..."
MISSING_DEPS=""

if ! python -c "import streamlit" 2>/dev/null; then
    MISSING_DEPS="$MISSING_DEPS streamlit"
fi
if ! python -c "import minio" 2>/dev/null; then
    MISSING_DEPS="$MISSING_DEPS minio"
fi
if ! python -c "import neo4j" 2>/dev/null; then
    MISSING_DEPS="$MISSING_DEPS neo4j"
fi
if ! python -c "import yaml" 2>/dev/null; then
    MISSING_DEPS="$MISSING_DEPS pyyaml"
fi

if [ -n "$MISSING_DEPS" ]; then
    log_info "Installiere fehlende Dependencies:$MISSING_DEPS"
    pip install $MISSING_DEPS pillow requests scikit-learn
fi

# Installiere Projekt-Dependencies
log_info "Installiere Projekt-Dependencies..."
pip install -e . --quiet 2>&1 | grep -v "already satisfied" || true

# Finale Prüfung
log_info "Prüfe alle Dependencies..."
python -c "import minio, neo4j, streamlit, yaml; print('[OK] Alle Dependencies verfügbar')" || {
    log_error "Einige Dependencies fehlen!"
    log_info "Bitte installieren Sie manuell: pip install minio neo4j streamlit pyyaml"
    exit 1
}

# Prüfe ob Port belegt ist
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    log_warn "Port 8501 ist bereits belegt"
    PID=$(lsof -ti :8501)
    log_info "Beende Prozess $PID..."
    kill $PID 2>/dev/null || true
    sleep 2
fi

# Starte Streamlit
log_info "Starte Streamlit App..."
log_info "App: http://localhost:8501"

cd "$PROJECT_ROOT"
streamlit run "$STREAMLIT_APP" --server.port 8501 --server.address 0.0.0.0
