# Ray Cluster Setup für Mac Studio Cluster

Anleitung zum Einrichten eines Ray Clusters für verteilte Face Tagging Verarbeitung über mehrere Mac Studio Nodes.

## Schnellstart

### 1. Ray installieren

```bash
cd /Users/blaubaer/Documents/Aphrodite/MacStudioCluster
source mlx_env/bin/activate
pip install ray[default]
```

### 2. Head Node starten (auf Mac Studio M4)

```bash
./ray_cluster/start_ray_cluster.sh head
```

Das startet:
- Ray Head Node auf Port 10001
- Ray Dashboard auf http://localhost:8265

### 3. Worker Nodes starten (auf anderen Macs)

Auf jedem weiteren Mac Studio:

```bash
# Ersetze <head-ip> mit der IP des Head Nodes
./ray_cluster/start_ray_cluster.sh worker <head-ip>:10001
```

Beispiel:
```bash
# Auf Mac Studio M3 (10.10.10.11)
./ray_cluster/start_ray_cluster.sh worker 10.10.10.12:10001
```

### 4. Cluster-Status prüfen

```bash
ray status
```

Oder im Browser: http://localhost:8265

## Verwendung

### Python API

```python
from ray_cluster.ray_pipeline import RayFaceTagPipeline

# Verbindung zu Remote Cluster
pipeline = RayFaceTagPipeline(ray_address="ray://10.10.10.12:10001")

try:
    # Cluster-Status
    status = pipeline.get_cluster_status()
    print(f"Nodes: {status['nodes']}")
    
    # Einzelnes Bild verarbeiten (verteilt)
    result = pipeline.process_photo_distributed("/path/to/image.jpg")
    
    # Batch-Verarbeitung (parallel über alle Nodes)
    results = pipeline.process_batch_distributed([
        "/path/to/image1.jpg",
        "/path/to/image2.jpg"
    ])
    
finally:
    pipeline.shutdown()
```

## GPU-Ressourcen-Sharing

Ray verteilt automatisch GPU-Ressourcen:

- **Face Detection:** 0.5 GPU pro Task
- **Embedding:** 0.5 GPU pro Task
- **Parallele Verarbeitung:** Mehrere Tasks gleichzeitig

### Beispiel: 2 Nodes mit je 1 GPU

- Node 1: 2 Face Detection Tasks parallel (je 0.5 GPU)
- Node 2: 2 Embedding Tasks parallel (je 0.5 GPU)
- **Gesamt:** 4 Tasks parallel über 2 Nodes

## Netzwerk-Konfiguration

### Firewall

Stelle sicher, dass folgende Ports offen sind:
- **10001:** Ray Head/Worker Kommunikation
- **8265:** Ray Dashboard
- **10002:** Ray Object Store

### macOS Firewall

```bash
# Ray Ports freigeben
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/ray
```

## Troubleshooting

### Worker kann Head nicht erreichen

1. Prüfe Netzwerk:
   ```bash
   ping <head-ip>
   ```

2. Prüfe Firewall:
   ```bash
   # Auf Head Node
   lsof -i :10001
   ```

3. Prüfe Ray Status:
   ```bash
   ray status
   ```

### GPU nicht erkannt

```bash
# Prüfe MLX
python -c "import mlx.core as mx; print(mx.default_device())"

# Ray GPU-Erkennung
ray status
```

### Port bereits belegt

```bash
# Stoppe Ray
./ray_cluster/stop_ray_cluster.sh
```

## Performance

### Lokal (1 Node)
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

Zugriff: http://localhost:8265

Zeigt:
- Cluster-Status
- Node-Ressourcen
- Task-Verteilung
- GPU-Nutzung
- Performance-Metriken

### Command Line

```bash
# Cluster-Status
ray status

# Verfügbare Ressourcen
ray exec ray://head:10001 "ray available_resources()"
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

## Weitere Informationen

- [Ray Documentation](https://docs.ray.io/)
- [Ray on Apple Silicon](https://docs.ray.io/en/latest/ray-core/configure.html#apple-silicon-m1-m2)
- [Ray Dashboard](https://docs.ray.io/en/latest/ray-core/ray-dashboard.html)


