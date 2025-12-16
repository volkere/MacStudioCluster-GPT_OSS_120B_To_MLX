#!/bin/bash
# Entrypoint für Worker Node Container

set -e

echo "[INFO] === Worker Node Start ==="
echo "[INFO] Node Type: ${NODE_TYPE:-worker}"
echo "[INFO] Head Node: ${RAY_HEAD_ADDRESS:-not set}"

# Setze Node-Typ
mkdir -p /app/.node_config
echo "{\"node_type\": \"${NODE_TYPE:-worker}\"}" > /app/.node_config.json

# Warte auf Head Node falls gesetzt
if [ -n "$RAY_HEAD_ADDRESS" ]; then
    echo "[INFO] Warte auf Head Node: $RAY_HEAD_ADDRESS"
    HEAD_HOST=$(echo $RAY_HEAD_ADDRESS | cut -d: -f1)
    HEAD_PORT=$(echo $RAY_HEAD_ADDRESS | cut -d: -f2)
    until python3 -c "import socket; s = socket.socket(); s.settimeout(1); s.connect(('$HEAD_HOST', $HEAD_PORT)); s.close()" 2>/dev/null; do
        echo "[INFO] Warte auf Head Node..."
        sleep 2
    done
    echo "[INFO] Head Node erreichbar"
fi

# Starte Services basierend auf Node-Typ
if [ "${NODE_TYPE:-worker}" = "worker" ]; then
    echo "[INFO] Starte Worker Services..."
    
    # Starte Face Detection Service
    echo "[INFO] Starte Face Detection Service..."
    python3 /app/services/face_detection_service.py &
    
    # Starte Embedding Service
    echo "[INFO] Starte Embedding Service..."
    python3 /app/services/embedding_service.py &
    
    # Starte Ray Worker
    if [ -n "$RAY_HEAD_ADDRESS" ]; then
        echo "[INFO] Starte Ray Worker..."
        cd /app
        source /app/venv/bin/activate 2>/dev/null || true
        ray start --address="$RAY_HEAD_ADDRESS" \
            --num-cpus=${RAY_CPUS:-16} \
            --num-gpus=${RAY_GPUS:-1} \
            --disable-usage-stats &
    fi
fi

# Health Check Endpoint
python3 -m http.server 8080 --directory /app &

echo "[INFO] === Worker Node bereit ==="
echo "[INFO] Services laufen im Hintergrund"

# Halte Container am Leben
tail -f /dev/null


