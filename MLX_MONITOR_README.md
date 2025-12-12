# MLX Monitoring Tool

Ein einfaches Tool zum Überwachen von Apple MLX auf deinem Mac Studio.

## Installation

MLX ist in einem virtuellen Environment installiert:
```bash
# Environment wurde bereits erstellt
# mlx_env/bin/activate
```

## Verwendung

### Einfache Verwendung (mit Wrapper-Script)

```bash
# Einmaliger Status-Check
./mlx_monitor.sh

# Performance-Test
./mlx_monitor.sh --test

# Monitoring
./mlx_monitor.sh --monitor
```

### Manuelle Verwendung (mit Environment-Aktivierung)

```bash
# Environment aktivieren
source mlx_env/bin/activate

# Einmaliger Status-Check
python mlx_monitor.py
```

### JSON-Output

```bash
python3 mlx_monitor.py --json
```

### Kontinuierliches Monitoring

```bash
# Alle 1 Sekunde aktualisieren (Standard)
python3 mlx_monitor.py --monitor

# Alle 0.5 Sekunden aktualisieren
python3 mlx_monitor.py --monitor --interval 0.5

# Für 60 Sekunden überwachen
python3 mlx_monitor.py --monitor --duration 60
```

### Performance-Test

```bash
# Standard-Test (100 Iterationen)
python3 mlx_monitor.py --test

# Mit mehr Iterationen
python3 mlx_monitor.py --test --iterations 200
```

## Verfügbare Optionen

- `--monitor, -m`: Startet kontinuierliches Monitoring
- `--interval, -i`: Intervall in Sekunden (Standard: 1.0)
- `--duration, -d`: Dauer des Monitorings in Sekunden
- `--json, -j`: Output im JSON-Format
- `--test, -t`: Führt einen Performance-Test durch
- `--iterations`: Anzahl der Iterationen für den Performance-Test

## Beispiele

```bash
# Status anzeigen
python3 mlx_monitor.py

# 10 Sekunden überwachen, alle 0.5 Sekunden
python3 mlx_monitor.py --monitor --interval 0.5 --duration 10

# Performance-Test mit 200 Iterationen
python3 mlx_monitor.py --test --iterations 200

# JSON-Output für Scripting
python3 mlx_monitor.py --json > mlx_status.json
```

## Hinweise

- **Memory-Info:** Detaillierte Memory-Informationen sind in MLX noch nicht vollständig verfügbar. Für detaillierte Memory-Überwachung nutze den macOS Activity Monitor.
- **Device-Info:** Das Tool zeigt das Standard-Device (meist GPU) an.
- **Performance-Test:** Der Test führt Matrix-Multiplikationen durch, um die MLX-Performance zu messen.

## Alternative Monitoring-Tools

Für detailliertere System-Überwachung:

1. **Activity Monitor** (macOS): 
   - Zeigt CPU, Memory, GPU-Nutzung
   - Menü: Applications > Utilities > Activity Monitor

2. **htop** (Terminal):
   ```bash
   brew install htop
   htop
   ```

3. **iStat Menus** (kommerziell):
   - Detailliertes System-Monitoring
   - https://bjango.com/mac/istatmenus/

4. **Stats** (Open Source):
   ```bash
   brew install --cask stats
   ```

## MLX-spezifische Monitoring

MLX selbst bietet derzeit keine umfassenden Monitoring-Tools. Das `mlx_monitor.py` Script nutzt die verfügbaren MLX-APIs:

- `mx.default_device()` - Zeigt das Standard-Device
- `mx.metal.get_memory_info()` - Memory-Informationen (wenn verfügbar)

Für zukünftige Updates, siehe: https://github.com/ml-explore/mlx

