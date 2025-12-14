# Mac Studio Cluster - Face Tagging System

Vollständiges Face Tagging System für Mac Studio Cluster mit MLX-Optimierung, verteilter Verarbeitung über Ray und KI-gestützter Annotation.

## 📋 Inhaltsverzeichnis

- [Übersicht](#übersicht)
- [Architektur](#architektur)
- [Installation](#installation)
- [Cluster Setup](#cluster-setup)
- [Verwendung](#verwendung)
- [Komponenten](#komponenten)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)

## 🎯 Übersicht

Dieses System ermöglicht:

- **Face Detection** mit MLX-Optimierung auf Apple Silicon
- **Embedding-Generierung** für Gesichts-Wiedererkennung
- **Clustering** ähnlicher Gesichter
- **KI-Annotation** mit GPT-OSS-120B / Llama Models
- **Graph-Datenbank** (Neo4j) für Beziehungen
- **Verteilte Verarbeitung** über mehrere Mac Studio Nodes mit Ray
- **GPU-Ressourcen-Sharing** zwischen Nodes

## 🏗️ Architektur

### System-Komponenten

```
┌─────────────────────────────────────────────────────────────┐
│                    Mac Studio Cluster                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Mac Studio  │  │  Mac Studio  │  │  Mac Studio   │     │
│  │     M3       │  │     M4       │  │   (weitere)   │     │
│  │              │  │              │  │              │     │
│  │ Ray Worker   │  │ Ray Head     │  │ Ray Worker   │     │
│  │ Face/Embed   │  │ Dashboard    │  │ Face/Embed   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Ray Cluster (Port 10001)                │   │
│  │         GPU-Ressourcen-Sharing & Load Balancing     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Services   │  │   Services   │  │   Services    │     │
│  │              │  │              │  │              │     │
│  │ Face Detect  │  │  Embedding   │  │  LLM (exo)    │     │
│  │  Port 5001   │  │  Port 5002   │  │  Port 8000    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │    minIO     │  │    Neo4j     │                        │
│  │  Port 9000   │  │  Port 7687   │                        │
│  └──────────────┘  └──────────────┘                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Verarbeitungspipeline

```
Bild Upload → minIO (incoming)
    ↓
Face Detection (MLX, verteilt über Ray)
    ↓
Face Crops → minIO (crops)
    ↓
Embedding-Generierung (ArcFace/MLX, verteilt über Ray)
    ↓
Clustering (DBSCAN)
    ↓
LLM-Annotation (GPT-OSS-120B / Llama)
    ↓
Neo4j Graph-Speicherung
    ↓
Fertig ✓
```

## 🚀 Installation

### Voraussetzungen

- **macOS:** 12.3+ (für MPS/MLX Support)
- **Python:** 3.10+ (empfohlen: 3.12)
- **RAM:** 64GB+ empfohlen (128GB für GPT-OSS-120B)
- **Hardware:** Apple Silicon (M1/M2/M3/M4)
- **Netzwerk:** Alle Macs im gleichen Netzwerk

### Schritt 1: Repository klonen

```bash
git clone https://github.com/USERNAME/MacStudioCluster.git
cd MacStudioCluster
```

### Schritt 2: Virtual Environment erstellen

```bash
# Erstelle mlx_env
python3 -m venv mlx_env
source mlx_env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Schritt 3: Dependencies installieren

```bash
# Installiere alle Dependencies
pip install -e .

# Oder manuell
pip install mlx>=0.29.0 mlx-lm>=0.28.0 numpy pillow minio neo4j requests scikit-learn pyyaml ray[default] flask
```

### Schritt 4: exo Framework (optional, für LLM)

```bash
# exo ist bereits als Submodule enthalten
cd exo
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cd ..
```

## 🌐 VLAN-Konfiguration (Optional)

Für Multi-Mac Cluster mit Netzwerk-Isolierung:

```bash
# Head Node (Management VLAN)
sudo ./network/setup_vlan.sh head 10.30.30.10

# Worker Node (Worker + Management VLAN)
sudo ./network/setup_vlan.sh worker 10.30.30.11 10.10.10.11

# Storage Node (Storage + Management VLAN)
sudo ./network/setup_vlan.sh storage 10.30.30.100 10.20.20.100
```

Siehe [VLAN_SETUP.md](VLAN_SETUP.md) für detaillierte Anleitung.

## 🔧 Cluster Setup

### Option A: Einzelner Mac (Lokaler Cluster)

Für Testing oder kleine Workloads:

```bash
# 1. Services starten
./services/start_services.sh

# 2. Ray Cluster starten (lokal)
./ray_cluster/start_ray_cluster.sh head

# 3. Pipeline verwenden
python -m pipeline.cli image /path/to/image.jpg
```

### Option B: Multi-Mac Cluster

#### Schritt 1: Head Node einrichten (auf Mac Studio M4)

```bash
# 1. Repository klonen und installieren (siehe Installation)
cd MacStudioCluster
source mlx_env/bin/activate

# 2. Head Node starten
./ray_cluster/start_ray_cluster.sh head

# 3. Services starten
./services/start_services.sh

# 4. IP-Adresse notieren
ifconfig | grep "inet " | grep -v 127.0.0.1
# Beispiel: 10.10.10.12
```

**Wichtig:** Notiere die IP-Adresse des Head Nodes!

#### Schritt 2: Worker Nodes einrichten (auf anderen Macs)

Auf jedem weiteren Mac Studio:

```bash
# 1. Repository klonen und installieren (siehe Installation)
cd MacStudioCluster
source mlx_env/bin/activate

# 2. Worker Node starten (ersetze <head-ip> mit IP des Head Nodes)
./ray_cluster/start_ray_cluster.sh worker <head-ip>:10001

# Beispiel:
# ./ray_cluster/start_ray_cluster.sh worker 10.10.10.12:10001
```

#### Schritt 3: Cluster-Status prüfen

Auf dem Head Node:

```bash
ray status
```

Oder im Browser: http://localhost:8265 (Ray Dashboard)

### Netzwerk-Konfiguration

#### Firewall

Stelle sicher, dass folgende Ports offen sind:

- **10001:** Ray Head/Worker Kommunikation
- **8265:** Ray Dashboard
- **5001:** Face Detection Service
- **5002:** Embedding Service
- **8000:** LLM Service (exo)
- **9000:** minIO
- **7687:** Neo4j

#### macOS Firewall

```bash
# System Preferences → Security & Privacy → Firewall
# Oder via Terminal:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/ray
```

#### Netzwerk-Test

```bash
# Von Worker zu Head
ping <head-ip>

# Port-Test
nc -zv <head-ip> 10001
```

## 🖥️ Admin Dashboard

Web-basiertes Interface für Installation, Konfiguration und Verwaltung:

```bash
cd admin
./start_admin.sh
```

Dann öffne im Browser: **http://localhost:8080**

**Features:**
- ✅ Installation aller Dependencies
- ✅ Service-Management (Start/Stop)
- ✅ VLAN-Setup
- ✅ Konfiguration
- ✅ Cluster-Status und Monitoring

Siehe [Admin README](admin/README.md) für Details.

## 📖 Verwendung

### CLI (Command Line)

#### Einzelnes Bild verarbeiten

```bash
# Lokale Pipeline
python -m pipeline.cli image /path/to/image.jpg

# Ray-basierte Pipeline (verteilt)
python -c "
from ray_cluster.ray_pipeline import RayFaceTagPipeline
pipeline = RayFaceTagPipeline(ray_address='ray://<head-ip>:10001')
result = pipeline.process_photo_distributed('/path/to/image.jpg')
print(f'Gesichter: {len(result[\"faces\"])}')
pipeline.shutdown()
"
```

#### Batch-Verarbeitung

```bash
# Lokale Pipeline
python -m pipeline.cli batch image1.jpg image2.jpg image3.jpg

# Ray-basierte Pipeline (verteilt)
python -c "
from ray_cluster.ray_pipeline import RayFaceTagPipeline
pipeline = RayFaceTagPipeline(ray_address='ray://<head-ip>:10001')
results = pipeline.process_batch_distributed([
    '/path/to/image1.jpg',
    '/path/to/image2.jpg',
    '/path/to/image3.jpg'
])
print(f'Verarbeitet: {len(results)} Bilder')
pipeline.shutdown()
"
```

### Python API

#### Lokale Pipeline

```python
from pipeline.face_tag_pipeline import FaceTagPipeline

pipeline = FaceTagPipeline()

# Einzelnes Bild
result = pipeline.process_photo("/path/to/image.jpg")

# Batch
results = pipeline.process_batch(["/path/to/img1.jpg", "/path/to/img2.jpg"])

pipeline.close()
```

#### Ray-basierte Pipeline (verteilt)

```python
from ray_cluster.ray_pipeline import RayFaceTagPipeline

# Verbindung zu Remote Cluster
pipeline = RayFaceTagPipeline(ray_address="ray://10.10.10.12:10001")

try:
    # Cluster-Status
    status = pipeline.get_cluster_status()
    print(f"Nodes: {status['nodes']}")
    print(f"Resources: {status['cluster_resources']}")
    
    # Verteilte Verarbeitung
    result = pipeline.process_photo_distributed("/path/to/image.jpg")
    
    # Batch über alle Nodes
    results = pipeline.process_batch_distributed([
        "/path/to/image1.jpg",
        "/path/to/image2.jpg"
    ])
    
finally:
    pipeline.shutdown()
```

## 🧩 Komponenten

### Services

| Service | Port | Beschreibung |
|---------|------|--------------|
| Face Detection | 5001 | MLX-optimierte Gesichtserkennung |
| Embedding | 5002 | ArcFace/MLX Embedding-Generierung |
| LLM (exo) | 8000 | ChatGPT-kompatible LLM API |
| minIO | 9000 | Objektspeicher für Bilder |
| Neo4j | 7687 | Graph-Datenbank |
| Ray Dashboard | 8265 | Cluster-Monitoring |

### Pipeline-Module

- **`pipeline/face_tag_pipeline.py`** - Haupt-Pipeline
- **`pipeline/face_detection.py`** - Face Detection Service Client
- **`pipeline/embeddings.py`** - Embedding Service Client
- **`pipeline/clustering.py`** - DBSCAN Clustering
- **`pipeline/llm_service.py`** - LLM Service Client
- **`pipeline/neo4j_client.py`** - Neo4j Client
- **`pipeline/minio_client.py`** - minIO Client

### Ray Cluster

- **`ray_cluster/ray_face_detection.py`** - Ray Remote Functions für Face Detection
- **`ray_cluster/ray_embeddings.py`** - Ray Remote Functions für Embeddings
- **`ray_cluster/ray_pipeline.py`** - Ray-basierte Pipeline

## ⚡ Performance

### Lokale Verarbeitung (1 Node)

- **Face Detection:** ~0.5-0.8s pro Bild
- **Embedding:** ~0.1-0.15s pro Gesicht
- **Durchsatz:** ~1 Bild/Sekunde

### Verteilt (2 Nodes)

- **Durchsatz:** ~2 Bilder/Sekunde
- **2 GPUs parallel genutzt**
- **Automatische Lastverteilung**

### Skalierung

| Nodes | Durchsatz | GPUs |
|-------|-----------|------|
| 1 | ~1 Bild/s | 1 |
| 2 | ~2 Bilder/s | 2 |
| 3 | ~3 Bilder/s | 3 |
| 4 | ~4 Bilder/s | 4 |

**Linear skalierbar!**

## 🔍 Monitoring

### Ray Dashboard

Zugriff: http://localhost:8265 (auf Head Node)

Zeigt:
- Cluster-Status
- Node-Ressourcen
- Task-Verteilung
- GPU-Nutzung
- Performance-Metriken

### Service Health Checks

```bash
# Face Detection
curl http://localhost:5001/health

# Embedding
curl http://localhost:5002/health

# LLM (exo)
curl http://localhost:8000/v1/models
```

### Logs

```bash
# Service Logs
tail -f services/face_detection.log
tail -f services/embedding.log
tail -f services/exo.log

# Pipeline Logs
tail -f pipeline.log
tail -f ray_pipeline.log
```

## 🛠️ Troubleshooting

### Ray Cluster

#### Worker kann Head nicht erreichen

1. **Netzwerk prüfen:**
   ```bash
   ping <head-ip>
   nc -zv <head-ip> 10001
   ```

2. **Firewall prüfen:**
   ```bash
   # Auf Head Node
   lsof -i :10001
   ```

3. **Ray Status:**
   ```bash
   ray status
   ```

#### GPU nicht erkannt

```bash
# MLX prüfen
python -c "import mlx.core as mx; print(mx.default_device())"

# Ray GPU-Erkennung
ray status
```

### Services

#### Service startet nicht

```bash
# Prüfe Logs
tail -f services/<service>.log

# Prüfe Port
lsof -i :<port>

# Stoppe alle Services
./services/stop_services.sh

# Starte neu
./services/start_services.sh
```

#### Port bereits belegt

```bash
# Finde Prozess
lsof -i :<port>

# Beende Prozess
kill -9 <pid>
```

### Pipeline

#### Import-Fehler

```bash
# Stelle sicher, dass mlx_env aktiviert ist
source mlx_env/bin/activate

# Prüfe Installation
pip list | grep -E "(mlx|ray|minio|neo4j)"
```

#### Konfiguration

Prüfe `pipeline/config.yaml`:
- Service URLs korrekt?
- Credentials korrekt?
- Ports verfügbar?

## 📚 Weitere Dokumentation

- **[Admin Dashboard](admin/README.md)** - Web-Interface für Installation und Verwaltung
- **[VLAN Setup](VLAN_SETUP.md)** - Multi-VLAN Konfiguration für Management, Worker und Storage
- **[Pipeline README](pipeline/README.md)** - Detaillierte Pipeline-Dokumentation
- **[Ray Cluster Setup](RAY_CLUSTER_SETUP.md)** - Ray Cluster Setup-Anleitung
- **[Installation Guide](INSTALLATION.md)** - Vollständige Installationsanleitung
- **[Services README](services/README.md)** - Service-Dokumentation
- **[Network README](network/README.md)** - Netzwerk- und VLAN-Dokumentation
- **[MLX Model Loading](MLX_MODEL_LOADING.md)** - MLX Model Konvertierung
- **[Face Tagging Software](face_tag_software.md)** - Software-Architektur
- **[Face Tagging Hardware](face_tag_hardware.md)** - Hardware-Architektur

## 🤝 Contributing

Beiträge sind willkommen! Bitte erstelle ein Issue oder Pull Request.

## 📄 License

Siehe LICENSE Dateien in den jeweiligen Unterprojekten.

## 🔗 Links

- [MLX Framework](https://github.com/ml-explore/mlx)
- [Ray Framework](https://docs.ray.io/)
- [exo Framework](https://github.com/exo-explore/exo)
- [Neo4j](https://neo4j.com/)
- [minIO](https://min.io/)

---

**Hinweis:** Die Modell-Gewichte (`.safetensors` Dateien) sind nicht im Repository enthalten, da sie zu groß sind. Bitte lade sie separat von Hugging Face herunter.
