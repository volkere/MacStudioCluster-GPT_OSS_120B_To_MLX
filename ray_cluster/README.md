# Ray Cluster für Mac Studio Face Tagging

Ray-basierte verteilte Verarbeitung für Face Tagging über mehrere Mac Studio Nodes mit GPU-Ressourcen-Sharing.

## Übersicht

Ray ermöglicht:
- **Verteiltes Computing** über mehrere Mac Studio Nodes
- **GPU-Ressourcen-Sharing** für MLX-Modelle
- **Automatische Lastverteilung** zwischen Nodes
- **Skalierbare Pipeline** für große Bildmengen

## Architektur

```
Head Node (Mac Studio M4)
├── Ray Dashboard (Port 8265)
├── Ray Head (Port 10001)
└── Koordiniert Worker Nodes

Worker Nodes
├── Mac Studio M3 (10.10.10.11)
│   ├── Face Detection Actor
│   └── Embedding Actor
└── Mac Studio M4 (10.10.10.12)
    ├── Face Detection Actor
    └── Embedding Actor
```

## Installation

```bash
# Ray installieren
source mlx_env/bin/activate
pip install ray[default]
```

## Cluster Setup

### 1. Head Node starten (auf Mac Studio M4)

```bash
cd /Users/blaubaer/Documents/Aphrodite/MacStudioCluster
./ray_cluster/start_ray_cluster.sh head
```

Das startet:
- Ray Head Node auf Port 10001
- Ray Dashboard auf Port 8265
- Verfügbar unter: http://localhost:8265

### 2. Worker Nodes starten (auf anderen Macs)

```bash
# Auf Mac Studio M3 (10.10.10.11)
./ray_cluster/start_ray_cluster.sh worker 10.10.10.12:10001

# Auf weiteren Macs
./ray_cluster/start_ray_cluster.sh worker <head-ip>:10001
```

### 3. Cluster-Status prüfen

```bash
ray status
```

Oder im Dashboard: http://localhost:8265

## Verwendung

### Python API

```python
from ray_cluster.ray_pipeline import RayFaceTagPipeline

# Pipeline initialisieren (verbindet zu Head Node)
pipeline = RayFaceTagPipeline(ray_address="ray://10.10.10.12:10001")

try:
    # Cluster-Status
    status = pipeline.get_cluster_status()
    print(f"Nodes: {status['nodes']}")
    print(f"Resources: {status['cluster_resources']}")
    
    # Einzelnes Bild verarbeiten
    result = pipeline.process_photo_distributed("/path/to/image.jpg")
    print(f"Gesichter: {len(result['faces'])}")
    
    # Batch-Verarbeitung (parallel über alle Nodes)
    results = pipeline.process_batch_distributed([
        "/path/to/image1.jpg",
        "/path/to/image2.jpg",
        "/path/to/image3.jpg"
    ])
    
finally:
    pipeline.shutdown()
```

### Lokaler Cluster (für Testing)

```python
# Startet lokalen Ray Cluster
pipeline = RayFaceTagPipeline()  # Kein ray_address = lokaler Cluster
```

## GPU-Ressourcen-Management

Ray verteilt automatisch GPU-Ressourcen:

- **Face Detection:** 0.5 GPU pro Task
- **Embedding:** 0.5 GPU pro Task
- **Parallele Verarbeitung:** Mehrere Tasks gleichzeitig auf verschiedenen Nodes

### Resource Allocation

```python
# In ray_face_detection.py
@ray.remote(num_gpus=0.5, num_cpus=2)
def detect_faces_remote(image_bytes: bytes):
    # Nutzt 0.5 GPU auf einem Node
    pass

# In ray_embeddings.py
@ray.remote(num_gpus=0.5, num_cpus=2)
def generate_embedding_remote(face_crop_bytes: bytes):
    # Nutzt 0.5 GPU auf einem Node
    pass
```

## Ray Actors

Ray Actors ermöglichen persistente Modelle auf jedem Node:

```python
# Face Detection Actor (lädt Model einmal, verwendet es mehrfach)
face_actor = FaceDetectionActor.remote()

# Embedding Actor (lädt Model einmal, verwendet es mehrfach)
embedding_actor = EmbeddingActor.remote()
```

## Performance

### Lokale Verarbeitung (1 Node)
- ~1 Bild/Sekunde
- 1 GPU vollständig genutzt

### Verteilt (2 Nodes)
- ~2 Bilder/Sekunde
- 2 GPUs parallel genutzt
- Automatische Lastverteilung

### Skalierung
- **3 Nodes:** ~3 Bilder/Sekunde
- **4 Nodes:** ~4 Bilder/Sekunde
- Linear skalierbar

## Monitoring

### Ray Dashboard

Zugriff auf: http://localhost:8265

Zeigt:
- Cluster-Status
- Node-Ressourcen
- Task-Verteilung
- GPU-Nutzung
- Performance-Metriken

### Python API

```python
# Cluster-Status
status = pipeline.get_cluster_status()
print(status)

# Verfügbare Ressourcen
import ray
print(ray.available_resources())
print(ray.cluster_resources())
```

## Troubleshooting

### Worker kann Head nicht erreichen

```bash
# Prüfe Firewall
# Stelle sicher, dass Port 10001 offen ist

# Prüfe Netzwerk
ping <head-ip>

# Prüfe Ray Status
ray status
```

### GPU nicht erkannt

```bash
# Prüfe MLX
python -c "import mlx.core as mx; print(mx.default_device())"

# Ray GPU-Erkennung
ray status  # Zeigt verfügbare GPUs
```

### Port bereits belegt

```bash
# Stoppe Ray
./ray_cluster/stop_ray_cluster.sh

# Oder manuell
ray stop --force
```

## Konfiguration

Anpassung in `ray_cluster/config.yaml`:

```yaml
ray:
  num_cpus: 16
  num_gpus: 1
  object_store_memory: 32000000000  # 32 GB

resources:
  face_detection:
    num_gpus: 0.5
  embedding:
    num_gpus: 0.5
```

## Integration mit Pipeline

Die Ray-Pipeline kann parallel zur normalen Pipeline verwendet werden:

```python
# Normale Pipeline (lokale Services)
from pipeline.face_tag_pipeline import FaceTagPipeline
pipeline = FaceTagPipeline()

# Ray-Pipeline (verteilt)
from ray_cluster.ray_pipeline import RayFaceTagPipeline
ray_pipeline = RayFaceTagPipeline(ray_address="ray://head:10001")
```

## Weitere Informationen

- [Ray Documentation](https://docs.ray.io/)
- [Ray on Apple Silicon](https://docs.ray.io/en/latest/ray-core/configure.html#apple-silicon-m1-m2)
- [Ray Dashboard](https://docs.ray.io/en/latest/ray-core/ray-dashboard.html)
