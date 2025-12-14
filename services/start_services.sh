#!/bin/bash
# Start-Script für alle Face Tagging Services
# Verwendet mlx_env für Python-Services

set -e

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SERVICES_DIR="$PROJECT_ROOT/services"
MLX_ENV="$PROJECT_ROOT/mlx_env"
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

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port ist belegt
    else
        return 1  # Port ist frei
    fi
}

wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    return 1
}

start_service() {
    local service_name=$1
    local script_path=$2
    local port=$3
    
    log_info "Starte $service_name..."
    
    # Prüfe ob Port belegt ist
    if check_port $port; then
        log_warn "Port $port ist bereits belegt"
        
        # Versuche Prozess auf Port zu finden und zu beenden
        local pid=$(lsof -ti :$port 2>/dev/null)
        if [ -n "$pid" ]; then
            log_info "Beende Prozess $pid auf Port $port..."
            kill $pid 2>/dev/null || true
            sleep 2
            
            # Prüfe erneut
            if check_port $port; then
                log_warn "Port $port immer noch belegt, erzwinge Beendigung..."
                kill -9 $pid 2>/dev/null || true
                sleep 1
            fi
        fi
        
        # Prüfe nochmal ob Port jetzt frei ist
        if check_port $port; then
            log_warn "Port $port ist immer noch belegt, überspringe $service_name"
            return 1
        fi
    fi
    
    # Starte Service im Hintergrund
    cd "$PROJECT_ROOT"
    source "$MLX_ENV/bin/activate"
    
    nohup python "$script_path" > "$PROJECT_ROOT/services/${service_name}.log" 2>&1 &
    local pid=$!
    echo "$service_name:$pid:$port" >> "$PID_FILE"
    
    log_info "$service_name gestartet (PID: $pid, Port: $port)"
    sleep 2  # Kurze Pause für Initialisierung
    
    return 0
}

start_exo() {
    log_info "Starte exo (LLM Service)..."
    
    if check_port 52415; then
        log_warn "Port 52415 ist bereits belegt, exo läuft möglicherweise bereits"
        return 1
    fi
    
    cd "$PROJECT_ROOT/exo"
    source .venv/bin/activate
    
    nohup exo --chatgpt-api-port 8000 --disable-tui > "$PROJECT_ROOT/services/exo.log" 2>&1 &
    local pid=$!
    echo "exo:$pid:8000" >> "$PID_FILE"
    
    log_info "exo gestartet (PID: $pid, Port: 8000)"
    sleep 5  # exo braucht etwas länger zum Starten
    
    return 0
}

# Hauptfunktion
main() {
    log_info "=== Face Tagging Services Start ==="
    
    # Prüfe mlx_env
    if [ ! -d "$MLX_ENV" ]; then
        log_error "mlx_env nicht gefunden: $MLX_ENV"
        log_info "Erstelle mlx_env..."
        cd "$PROJECT_ROOT"
        python3 -m venv mlx_env
        source "$MLX_ENV/bin/activate"
        pip install --upgrade pip
        pip install flask requests pillow numpy
    fi
    
    # Installiere Dependencies in mlx_env
    log_info "Installiere Dependencies..."
    source "$MLX_ENV/bin/activate"
    cd "$PROJECT_ROOT"
    pip install -q flask requests pillow numpy scikit-learn pyyaml || true
    
    # Erstelle PID-Datei
    mkdir -p "$PROJECT_ROOT/services"
    > "$PID_FILE"
    
    # Starte Services
    log_info "Starte Python-Services..."
    
    start_service "face_detection" "$SERVICES_DIR/face_detection_service.py" 5001
    start_service "embedding" "$SERVICES_DIR/embedding_service.py" 5002
    
    # Starte exo für LLM (falls verfügbar)
    if [ -d "$PROJECT_ROOT/exo" ]; then
        start_exo
    else
        log_warn "exo nicht gefunden, LLM-Service wird nicht gestartet"
    fi
    
    # Warte auf Services
    log_info "Warte auf Services..."
    sleep 3
    
    # Health Checks
    log_info "Führe Health Checks durch..."
    
    if wait_for_service "http://localhost:5001/health"; then
        log_info "[OK] Face Detection Service ist bereit"
    else
        log_warn "[FAIL] Face Detection Service antwortet nicht"
    fi
    
    if wait_for_service "http://localhost:5002/health"; then
        log_info "[OK] Embedding Service ist bereit"
    else
        log_warn "[FAIL] Embedding Service antwortet nicht"
    fi
    
    if wait_for_service "http://localhost:8000/v1/models"; then
        log_info "[OK] LLM Service (exo) ist bereit"
    else
        log_warn "[FAIL] LLM Service antwortet nicht"
    fi
    
    log_info ""
    log_info "=== Services Status ==="
    log_info "Face Detection:  http://localhost:5001"
    log_info "Embedding:        http://localhost:5002"
    log_info "LLM (exo):        http://localhost:8000"
    log_info ""
    log_info "Logs:"
    log_info "  Face Detection:  $PROJECT_ROOT/services/face_detection.log"
    log_info "  Embedding:       $PROJECT_ROOT/services/embedding.log"
    log_info "  exo:             $PROJECT_ROOT/services/exo.log"
    log_info ""
    log_info "PID-Datei: $PID_FILE"
    log_info ""
    log_info "Zum Stoppen: ./stop_services.sh"
}

main "$@"
