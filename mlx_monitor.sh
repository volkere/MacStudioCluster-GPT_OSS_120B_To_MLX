#!/bin/bash
# Wrapper-Script für MLX Monitor mit automatischer Environment-Aktivierung

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Aktiviere virtuelles Environment
source mlx_env/bin/activate

# Führe MLX Monitor aus
python mlx_monitor.py "$@"

