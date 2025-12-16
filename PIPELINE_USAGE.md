# Face Tagging Pipeline - Nutzungsanleitung

Vollständige Anleitung zur Verwendung der Face Tagging Pipeline.

## Übersicht

Die Face Tagging Pipeline verarbeitet Bilder durch folgende Schritte:

1. **Face Detection** - Erkennt Gesichter in Bildern
2. **Face Cropping** - Schneidet Gesichter aus
3. **Embedding-Generierung** - Erstellt Vektoren für Wiedererkennung
4. **Clustering** - Gruppiert ähnliche Gesichter
5. **LLM-Annotation** - Generiert Namen und Event-Informationen
6. **Neo4j-Speicherung** - Speichert Graph-Struktur
7. **minIO-Speicherung** - Speichert Bilder und Crops

## Voraussetzungen

### Services müssen laufen

Bevor du die Pipeline nutzen kannst, müssen folgende Services laufen:

```bash
# 1. Face Detection Service
./services/start_services.sh

# 2. Ray Cluster (optional, für verteilte Verarbeitung)
./ray_cluster/start_ray_cluster.sh head

# 3. minIO (falls nicht bereits läuft)
# 4. Neo4j (falls nicht bereits läuft)
```

### Konfiguration prüfen

Stelle sicher, dass `pipeline/config.yaml` korrekt konfiguriert ist:

```yaml
services:
  face_detection:
    url: "http://localhost:5001"  # Oder Worker-VLAN IP
  embedding:
    url: "http://localhost:5002"  # Oder Worker-VLAN IP
  llm:
    url: "http://localhost:8000"   # Oder Management-VLAN IP

minio:
  endpoint: "localhost:9000"  # Oder Storage-VLAN IP
  access_key: "minioadmin"
  secret_key: "minioadmin"

neo4j:
  uri: "bolt://localhost:7687"  # Oder Management-VLAN IP
  user: "neo4j"
  password: "password"
```

## Nutzungsmöglichkeiten

### 1. Command-Line Interface (CLI)

Die einfachste Methode ist die Verwendung des CLI-Tools.

#### Einzelnes Bild verarbeiten

```bash
# Aktiviere Virtual Environment
source mlx_env/bin/activate

# Verarbeite ein Bild
python -m pipeline.cli image /path/to/your/image.jpg

# Mit Upload zu minIO (Standard)
python -m pipeline.cli image /path/to/image.jpg --upload

# Ohne Upload zu minIO
python -m pipeline.cli image /path/to/image.jpg --no-upload

# JSON-Output für weitere Verarbeitung
python -m pipeline.cli image /path/to/image.jpg --json > result.json
```

**Output:**
```
[OK] Verarbeitung abgeschlossen
  Photo-ID: 550e8400-e29b-41d4-a716-446655440000
  Gesichter erkannt: 3
  Cluster erstellt: 2
```

#### Mehrere Bilder verarbeiten (Batch)

```bash
# Direkt mehrere Bilder
python -m pipeline.cli batch image1.jpg image2.jpg image3.jpg

# Aus Datei (eine Bildpfad pro Zeile)
echo -e "/path/to/image1.jpg\n/path/to/image2.jpg" > image_list.txt
python -m pipeline.cli batch --file image_list.txt

# JSON-Output
python -m pipeline.cli batch image1.jpg image2.jpg --json > batch_result.json
```

**Output:**
```
[OK] Batch-Verarbeitung abgeschlossen
  Bilder verarbeitet: 3
  Gesamt Gesichter: 8
  Gesamt Cluster: 5
```

#### Alle Bilder in minIO-Bucket verarbeiten

```bash
# Verarbeite alle Bilder im "incoming" Bucket
python -m pipeline.cli bucket incoming

# Anderer Bucket
python -m pipeline.cli bucket my-bucket-name

# JSON-Output
python -m pipeline.cli bucket incoming --json > bucket_result.json
```

### 2. Python API

Für erweiterte Nutzung oder Integration in eigene Scripts:

#### Basis-Verwendung

```python
from pipeline.face_tag_pipeline import FaceTagPipeline

# Pipeline initialisieren
pipeline = FaceTagPipeline()

try:
    # Einzelnes Bild verarbeiten
    result = pipeline.process_photo(
        "/path/to/image.jpg",
        upload_to_minio=True
    )
    
    print(f"Photo-ID: {result['photo_id']}")
    print(f"Gesichter: {len(result['faces'])}")
    print(f"Cluster: {len(result['clusters'])}")
    
finally:
    # Wichtig: Verbindungen schließen
    pipeline.close()
```

#### Batch-Verarbeitung

```python
from pipeline.face_tag_pipeline import FaceTagPipeline

pipeline = FaceTagPipeline()

try:
    # Mehrere Bilder
    image_paths = [
        "/path/to/image1.jpg",
        "/path/to/image2.jpg",
        "/path/to/image3.jpg"
    ]
    
    results = pipeline.process_batch(image_paths, upload_to_minio=True)
    
    for result in results:
        print(f"Bild: {result['image_path']}")
        print(f"  Gesichter: {len(result['faces'])}")
        print(f"  Cluster: {len(result['clusters']})")
        
finally:
    pipeline.close()
```

#### minIO-Bucket verarbeiten

```python
from pipeline.face_tag_pipeline import FaceTagPipeline

pipeline = FaceTagPipeline()

try:
    # Alle Bilder im Bucket verarbeiten
    results = pipeline.process_minio_bucket("incoming")
    
    print(f"Bilder verarbeitet: {len(results)}")
    
finally:
    pipeline.close()
```

### 3. Ray-basierte verteilte Verarbeitung

Für große Mengen von Bildern über mehrere Nodes:

```python
from ray_cluster.ray_pipeline import RayFaceTagPipeline

# Pipeline initialisieren (verbindet automatisch mit Ray Cluster)
pipeline = RayFaceTagPipeline()

try:
    # Verteilte Verarbeitung
    result = pipeline.process_photo_distributed("/path/to/image.jpg")
    
    # Batch über Cluster
    results = pipeline.process_batch_distributed([
        "/path/to/image1.jpg",
        "/path/to/image2.jpg"
    ])
    
    # Cluster-Status prüfen
    status = pipeline.get_cluster_status()
    print(f"Nodes: {status['nodes']}")
    print(f"CPUs: {status['cpus']}")
    print(f"GPUs: {status['gpus']}")
    
finally:
    pipeline.shutdown()
```

## Ergebnis-Struktur

Die Pipeline gibt ein Dictionary mit folgenden Informationen zurück:

```python
{
    "photo_id": "550e8400-e29b-41d4-a716-446655440000",  # Eindeutige ID
    "image_path": "/path/to/image.jpg",                  # Original-Pfad
    "minio_path": "incoming/photo_id.jpg",               # minIO-Pfad
    "timestamp": "2024-12-14T10:30:00",                  # Verarbeitungszeit
    "faces": [                                            # Erkannte Gesichter
        {
            "box": [100, 150, 200, 250],                 # Bounding Box [x, y, w, h]
            "confidence": 0.95,                           # Erkennungs-Confidence
            "embedding": [0.123, 0.456, ...],            # Embedding-Vektor
            "cluster_id": 0,                              # Zugehöriger Cluster
            "crop_path": "face-crops/photo_id_face_0.jpg" # Pfad zum Crop
        }
    ],
    "clusters": [                                         # Erstellte Cluster
        {
            "cluster_id": 0,
            "name": "Max Mustermann",                     # LLM-generierter Name
            "n_faces": 3,                                 # Anzahl Gesichter
            "event_info": {                               # Event-Informationen
                "date": "1980er",
                "event_type": "Geburtstag",
                "location": null
            },
            "representative_face": "crops/..."           # Repräsentatives Gesicht
        }
    ],
    "errors": []                                          # Fehler (falls vorhanden)
}
```

## Workflow-Beispiele

### Beispiel 1: Einzelnes Foto analysieren

```python
from pipeline.face_tag_pipeline import FaceTagPipeline
import json

pipeline = FaceTagPipeline()

try:
    result = pipeline.process_photo("family_photo.jpg")
    
    # Speichere Ergebnis
    with open("result.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Zeige Zusammenfassung
    print(f"Gesichter erkannt: {len(result['faces'])}")
    for cluster in result['clusters']:
        print(f"  - {cluster['name']}: {cluster['n_faces']} Gesichter")
        
finally:
    pipeline.close()
```

### Beispiel 2: Foto-Ordner verarbeiten

```python
from pathlib import Path
from pipeline.face_tag_pipeline import FaceTagPipeline

pipeline = FaceTagPipeline()

try:
    # Alle JPG-Dateien im Ordner
    photo_dir = Path("/path/to/photos")
    image_paths = list(photo_dir.glob("*.jpg"))
    
    # Batch-Verarbeitung
    results = pipeline.process_batch(
        [str(p) for p in image_paths],
        upload_to_minio=True
    )
    
    # Statistiken
    total_faces = sum(len(r['faces']) for r in results)
    total_clusters = sum(len(r['clusters']) for r in results)
    
    print(f"Verarbeitet: {len(results)} Bilder")
    print(f"Gesichter: {total_faces}")
    print(f"Cluster: {total_clusters}")
    
finally:
    pipeline.close()
```

### Beispiel 3: Kontinuierliche Verarbeitung aus minIO

```python
from pipeline.face_tag_pipeline import FaceTagPipeline
import time

pipeline = FaceTagPipeline()

try:
    while True:
        # Verarbeite alle neuen Bilder im incoming Bucket
        results = pipeline.process_minio_bucket("incoming")
        
        if results:
            print(f"Verarbeitet: {len(results)} neue Bilder")
        
        # Warte 60 Sekunden
        time.sleep(60)
        
finally:
    pipeline.close()
```

## Erweiterte Nutzung

### Custom Konfiguration

```python
from pipeline.face_tag_pipeline import FaceTagPipeline

# Eigene Config-Datei verwenden
pipeline = FaceTagPipeline(config_path="/path/to/custom_config.yaml")
```

### Fehlerbehandlung

```python
from pipeline.face_tag_pipeline import FaceTagPipeline

pipeline = FaceTagPipeline()

try:
    result = pipeline.process_photo("image.jpg")
    
    # Prüfe auf Fehler
    if result.get('errors'):
        print(f"Fehler aufgetreten: {result['errors']}")
    
    # Verarbeite trotzdem die erfolgreichen Gesichter
    if result['faces']:
        print(f"Erfolgreich: {len(result['faces'])} Gesichter erkannt")
        
finally:
    pipeline.close()
```

### Neo4j-Abfragen

Nach der Verarbeitung kannst du die Daten in Neo4j abfragen:

```python
from pipeline.neo4j_client import Neo4jClient
import yaml

# Lade Config
with open("pipeline/config.yaml") as f:
    config = yaml.safe_load(f)

neo4j = Neo4jClient(config)

# Finde alle Personen
query = "MATCH (p:Person) RETURN p.name, p.cluster_id"
results = neo4j.execute_cypher(query)

for row in results:
    print(f"Person: {row['p.name']}, Cluster: {row['p.cluster_id']}")

neo4j.close()
```

## Performance-Tipps

### Batch-Verarbeitung nutzen

Statt einzelne Bilder nacheinander zu verarbeiten:

```python
# Schlecht: Einzelne Verarbeitung
for image in images:
    pipeline.process_photo(image)  # Langsam

# Gut: Batch-Verarbeitung
pipeline.process_batch(images)  # Schneller
```

### Ray Cluster für große Mengen

Für sehr große Bildmengen (>100 Bilder):

```python
from ray_cluster.ray_pipeline import RayFaceTagPipeline

pipeline = RayFaceTagPipeline()
results = pipeline.process_batch_distributed(large_image_list)
```

### minIO Upload optimieren

Wenn Bilder bereits lokal sind, kannst du Upload überspringen:

```python
result = pipeline.process_photo(
    "image.jpg",
    upload_to_minio=False  # Schneller, wenn Bild bereits lokal
)
```

## Troubleshooting

### "Service nicht erreichbar"

```bash
# Prüfe ob Services laufen
curl http://localhost:5001/health  # Face Detection
curl http://localhost:5002/health  # Embedding
curl http://localhost:8000/v1/models  # LLM
```

### "Neo4j-Verbindungsfehler"

```bash
# Prüfe Neo4j
neo4j status

# Prüfe Credentials in config.yaml
```

### "minIO-Fehler"

```bash
# Prüfe minIO
curl http://localhost:9000/minio/health/live

# Prüfe Buckets
# minIO Console: http://localhost:9001
```

### Langsame Verarbeitung

1. **Ray Cluster nutzen** für verteilte Verarbeitung
2. **Batch-Größe erhöhen** in `config.yaml`:
   ```yaml
   processing:
     batch_size: 20  # Statt 10
   ```
3. **Services auf Worker Nodes** auslagern

## Weitere Ressourcen

- [Pipeline README](pipeline/README.md)
- [CLI Dokumentation](pipeline/cli.py)
- [Face Tagging Software](face_tag_software.md)
- [Ray Cluster Setup](RAY_CLUSTER_SETUP.md)
