# Installation Guide - Mac Studio Cluster

Schritt-für-Schritt Anleitung zur Installation des Face Tagging Systems auf mehreren Mac Studio Nodes.

## 📋 Übersicht

Diese Anleitung führt dich durch:
1. Installation auf einem einzelnen Mac
2. Setup eines Multi-Mac Clusters
3. Konfiguration aller Services
4. Verifikation der Installation

## 🖥️ Voraussetzungen

### Hardware

- **Mac Studio** mit Apple Silicon (M1/M2/M3/M4)
- **RAM:** 64GB+ (128GB empfohlen für GPT-OSS-120B)
- **Netzwerk:** Alle Macs im gleichen Netzwerk (empfohlen: 10GbE)

### Software

- **macOS:** 12.3+ (für MPS/MLX Support)
- **Python:** 3.10+ (empfohlen: 3.12)
- **Git:** Für Repository-Klonen
- **Homebrew:** Optional, für zusätzliche Tools

## 📦 Installation auf einem Mac

### Schritt 1: Repository klonen

```bash
# Wähle ein Verzeichnis für das Projekt
cd ~/Documents  # oder ein anderes Verzeichnis deiner Wahl

# Klone das Repository
git clone https://github.com/USERNAME/MacStudioCluster.git
cd MacStudioCluster
```

### Schritt 2: Python Environment erstellen

```bash
# Erstelle Virtual Environment
python3 -m venv mlx_env

# Aktiviere Environment
source mlx_env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Schritt 3: Dependencies installieren

```bash
# Installiere alle Dependencies aus pyproject.toml
pip install -e .

# Oder manuell installieren:
pip install mlx>=0.29.0 \
            mlx-lm>=0.28.0 \
            numpy>=1.24.0 \
            pillow>=9.0.0 \
            minio>=7.0.0 \
            neo4j>=5.0.0 \
            requests>=2.28.0 \
            scikit-learn>=1.3.0 \
            pyyaml>=6.0 \
            ray[default]>=2.8.0 \
            flask
```

### Schritt 4: exo Framework (optional, für LLM)

```bash
# exo ist als Submodule enthalten
cd exo

# Erstelle Virtual Environment für exo
python3 -m venv .venv
source .venv/bin/activate

# Installiere exo
pip install -e .

cd ..
```

### Schritt 5: Verifikation

```bash
# Prüfe MLX Installation
python -c "import mlx.core as mx; print('MLX:', mx.__version__)"
python -c "import mlx.core as mx; print('Device:', mx.default_device())"

# Prüfe Ray Installation
ray --version

# Prüfe andere Dependencies
python -c "import numpy, pillow, minio, neo4j, ray; print('All dependencies OK')"
```

## 🔧 Multi-Mac Cluster Setup

### Übersicht

Für einen Multi-Mac Cluster benötigst du:
- **1 Head Node** (koordiniert den Cluster)
- **1+ Worker Nodes** (führen die Verarbeitung aus)

### Schritt 1: Head Node einrichten

Wähle einen Mac Studio als Head Node (empfohlen: stärkster Mac, z.B. M4).

#### 1.1 Installation

```bash
# Führe Installation durch (siehe oben)
cd MacStudioCluster
source mlx_env/bin/activate
```

#### 1.2 IP-Adresse notieren

```bash
# Finde IP-Adresse
ifconfig | grep "inet " | grep -v 127.0.0.1

# Oder
ipconfig getifaddr en0  # für WiFi
ipconfig getifaddr en1  # für Ethernet
```

**Wichtig:** Notiere diese IP-Adresse! (z.B. `10.10.10.12`)

#### 1.3 Head Node starten

```bash
# Starte Ray Head Node
./ray_cluster/start_ray_cluster.sh head

# Du solltest sehen:
# [INFO] Ray Head Node gestartet
# [INFO] Dashboard: http://localhost:8265
```

#### 1.4 Services starten

```bash
# Starte alle Services
./services/start_services.sh

# Prüfe Status
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:8000/v1/models
```

#### 1.5 Firewall konfigurieren

```bash
# macOS System Preferences → Security & Privacy → Firewall
# Oder via Terminal:

# Erlaube eingehende Verbindungen für Ray
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/ray
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /path/to/ray
```

**Wichtig:** Stelle sicher, dass Port 10001 für eingehende Verbindungen offen ist!

### Schritt 2: Worker Nodes einrichten

Wiederhole für jeden weiteren Mac Studio:

#### 2.1 Installation

```bash
# Führe Installation durch (siehe oben)
cd MacStudioCluster
source mlx_env/bin/activate
```

#### 2.2 Worker Node starten

```bash
# Starte Worker Node (ersetze <head-ip> mit IP des Head Nodes)
./ray_cluster/start_ray_cluster.sh worker <head-ip>:10001

# Beispiel:
# ./ray_cluster/start_ray_cluster.sh worker 10.10.10.12:10001

# Du solltest sehen:
# [INFO] Ray Worker Node gestartet
```

#### 2.3 Verifikation

```bash
# Prüfe Verbindung (auf Head Node)
ray status

# Du solltest alle Worker Nodes sehen
```

### Schritt 3: Cluster-Status prüfen

Auf dem Head Node:

```bash
# Ray Status
ray status

# Ray Dashboard im Browser öffnen
open http://localhost:8265
```

Du solltest sehen:
- Anzahl der Nodes
- Verfügbare Ressourcen (CPU, GPU, Memory)
- Aktive Tasks

## 🔍 Verifikation der Installation

### Test 1: Lokale Services

```bash
# Health Checks
curl http://localhost:5001/health | python3 -m json.tool
curl http://localhost:5002/health | python3 -m json.tool
curl http://localhost:8000/v1/models | head -20
```

### Test 2: Ray Cluster

```bash
# Ray Status
ray status

# Python Test
python3 << EOF
import ray
ray.init(address="ray://localhost:10001", ignore_reinit_error=True)
print("Ray Cluster:", ray.cluster_resources())
ray.shutdown()
EOF
```

### Test 3: Pipeline

```bash
# Test mit Beispiel-Bild (falls vorhanden)
python -m pipeline.cli image /path/to/test_image.jpg

# Oder Ray-basierte Pipeline
python3 << EOF
from ray_cluster.ray_pipeline import RayFaceTagPipeline
pipeline = RayFaceTagPipeline()
status = pipeline.get_cluster_status()
print("Cluster Status:", status)
pipeline.shutdown()
EOF
```

## 🔄 Services verwalten

### Services starten

```bash
# Alle Services
./services/start_services.sh

# Ray Cluster
./ray_cluster/start_ray_cluster.sh head  # Auf Head Node
./ray_cluster/start_ray_cluster.sh worker <head-ip>:10001  # Auf Worker Nodes
```

### Services stoppen

```bash
# Alle Services
./services/stop_services.sh

# Ray Cluster
./ray_cluster/stop_ray_cluster.sh
```

### Services neu starten

```bash
# Stoppe alle
./services/stop_services.sh
./ray_cluster/stop_ray_cluster.sh

# Starte neu
./services/start_services.sh
./ray_cluster/start_ray_cluster.sh head  # oder worker
```

## 🌐 Netzwerk-Konfiguration

### Ports

Stelle sicher, dass folgende Ports offen sind:

| Port | Service | Richtung |
|------|---------|----------|
| 10001 | Ray Head/Worker | Bidirektional |
| 8265 | Ray Dashboard | Eingehend (Head Node) |
| 5001 | Face Detection | Eingehend |
| 5002 | Embedding | Eingehend |
| 8000 | LLM (exo) | Eingehend |
| 9000 | minIO | Eingehend |
| 7687 | Neo4j | Eingehend |

### Firewall-Regeln

#### macOS Firewall

```bash
# System Preferences → Security & Privacy → Firewall → Firewall Options
# Füge folgende Apps hinzu:
# - Python (für Ray)
# - Terminal (für Services)
```

#### Router/Network

Falls Router-Firewall aktiv ist:
- Erlaube Kommunikation zwischen Macs im lokalen Netzwerk
- Port-Forwarding ist nicht nötig (nur lokales Netzwerk)

### Netzwerk-Test

```bash
# Von Worker zu Head
ping <head-ip>

# Port-Test
nc -zv <head-ip> 10001

# Ray Verbindung testen
ray status  # Auf Head Node
```

## 🐛 Troubleshooting

### Problem: Worker kann Head nicht erreichen

**Lösung:**
1. Prüfe Netzwerk: `ping <head-ip>`
2. Prüfe Firewall auf Head Node
3. Prüfe Port: `nc -zv <head-ip> 10001`
4. Prüfe Ray Status auf Head Node: `ray status`

### Problem: Port bereits belegt

**Lösung:**
```bash
# Finde Prozess
lsof -i :<port>

# Beende Prozess
kill -9 <pid>

# Oder stoppe alle Services
./services/stop_services.sh
./ray_cluster/stop_ray_cluster.sh
```

### Problem: MLX nicht verfügbar

**Lösung:**
```bash
# Prüfe MLX Installation
python -c "import mlx.core as mx; print(mx.default_device())"

# Neu installieren falls nötig
pip install --upgrade mlx mlx-lm
```

### Problem: Dependencies fehlen

**Lösung:**
```bash
# Aktiviere Environment
source mlx_env/bin/activate

# Installiere alle Dependencies
pip install -e .
```

## 📝 Nächste Schritte

Nach erfolgreicher Installation:

1. **Pipeline testen:** Siehe [README.md](README.md#verwendung)
2. **Monitoring einrichten:** Ray Dashboard auf http://localhost:8265
3. **Konfiguration anpassen:** `pipeline/config.yaml` und `ray_cluster/config.yaml`
4. **Modelle hinzufügen:** Siehe [MLX_MODEL_LOADING.md](MLX_MODEL_LOADING.md)

## 💡 Tipps

- **Automatischer Start:** Erstelle Launch Agents für automatischen Start nach Reboot
- **Monitoring:** Nutze Ray Dashboard für Cluster-Überwachung
- **Backup:** Sichere Konfigurationsdateien regelmäßig
- **Updates:** Halte Dependencies aktuell: `pip install --upgrade -e .`

## 📚 Weitere Ressourcen

- [Haupt-README](README.md)
- [Ray Cluster Setup](RAY_CLUSTER_SETUP.md)
- [Pipeline Dokumentation](pipeline/README.md)
- [Services Dokumentation](services/README.md)
