#!/bin/bash
# Entrypoint für Management Node Container

set -e

echo "[INFO] === Management Node Start ==="
echo "[INFO] Node Type: ${NODE_TYPE:-management}"

# Setze Node-Typ
mkdir -p /app/.node_config
echo "{\"node_type\": \"${NODE_TYPE:-management}\"}" > /app/.node_config.json

# Starte Services basierend auf Node-Typ
if [ "${NODE_TYPE:-management}" = "management" ]; then
    echo "[INFO] Starte Management Services..."
    
    # Starte Ray Head
    echo "[INFO] Starte Ray Head..."
    cd /app
    source /app/venv/bin/activate 2>/dev/null || true
    ray start --head \
        --port=6380 \
        --ray-client-server-port=10001 \
        --dashboard-host=0.0.0.0 \
        --dashboard-port=8265 \
        --num-cpus=${RAY_CPUS:-16} \
        --num-gpus=${RAY_GPUS:-1} \
        --disable-usage-stats &
    
    # Starte LLM Service (exo)
    echo "[INFO] Starte LLM Service (exo)..."
    if [ -d "/app/exo" ]; then
        cd /app/exo
        python3 -m exo.main --chatgpt-api-port 8000 --disable-tui &
    fi
    
    # Starte Admin Server
    echo "[INFO] Starte Admin Server..."
    cd /app
    python3 /app/admin/admin_server.py &
    
    # Starte Monitoring (optional)
    if [ "${ENABLE_MONITORING:-false}" = "true" ]; then
        echo "[INFO] Starte Monitoring Services..."
        /app/monitoring/start_prometheus.sh &
        /app/monitoring/start_metrics_collector.sh &
        /app/monitoring/start_grafana.sh &
    fi
fi

echo "[INFO] === Management Node bereit ==="
echo "[INFO] Services laufen im Hintergrund"

# Halte Container am Leben
tail -f /dev/null


