# Face Tagging Pipeline

Vollständige End-to-End Pipeline für Face Tagging mit MLX-Optimierung auf Apple Silicon.

## Übersicht

Die Pipeline verbindet alle Komponenten des Face Tagging Systems:

1. **Face Detection** (MLX-optimiert) - Erkennt Gesichter in Bildern
2. **Embedding-Generierung** (ArcFace/MLX) - Erstellt Embeddings für Gesichts-Wiedererkennung
3. **Clustering** (DBSCAN) - Gruppiert ähnliche Gesichter
4. **LLM-Annotation** (GPT-OSS-120B/MLX) - Generiert semantische Annotationen
5. **Neo4j Integration** - Speichert Graph-Struktur
6. **minIO Integration** - Objektspeicher für Bilder

## Installation

```bash
# Dependencies installieren
pip install -e .

# Oder mit pip
pip install mlx mlx-lm minio neo4j requests scikit-learn pyyaml pillow numpy
```

## Konfiguration

Die Pipeline verwendet `pipeline/config.yaml` für die Konfiguration. Passe die Service-Endpoints, Credentials und Parameter an deine Umgebung an:

```yaml
services:
  face_detection:
    url: "http://localhost:5001"
  embedding:
    url: "http://localhost:5002"
  llm:
    url: "http://localhost:8000"
    model: "gpt-oss-120b-4bit"

minio:
  endpoint: "localhost:9000"
  access_key: "minioadmin"
  secret_key: "minioadmin"

neo4j:
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: "password"
```

## Verwendung

### CLI-Tool

#### Einzelnes Bild verarbeiten

```bash
python -m pipeline.cli image /path/to/image.jpg
```

#### Mehrere Bilder verarbeiten

```bash
# Direkt
python -m pipeline.cli batch image1.jpg image2.jpg image3.jpg

# Aus Datei
python -m pipeline.cli batch --file image_list.txt
```

#### Alle Bilder in minIO-Bucket verarbeiten

```bash
python -m pipeline.cli bucket incoming
```

#### JSON-Output

```bash
python -m pipeline.cli image image.jpg --json > result.json
```

### Python API

```python
from pipeline.face_tag_pipeline import FaceTagPipeline

# Pipeline initialisieren
pipeline = FaceTagPipeline()

# Einzelnes Bild verarbeiten
result = pipeline.process_photo("/path/to/image.jpg")

# Batch-Verarbeitung
results = pipeline.process_batch([
    "/path/to/image1.jpg",
    "/path/to/image2.jpg"
])

# minIO-Bucket verarbeiten
results = pipeline.process_minio_bucket("incoming")

# Verbindungen schließen
pipeline.close()
```

## Pipeline-Flow

```
1. Upload → minIO (incoming bucket)
   ↓
2. Face Detection → Gesichter erkennen
   ↓
3. Face Crops → Gesichter ausschneiden
   ↓
4. Embeddings → Vektoren generieren
   ↓
5. Clustering → Ähnliche Gesichter gruppieren
   ↓
6. LLM-Annotation → Namen & Events generieren
   ↓
7. Neo4j → Graph-Struktur speichern
   ↓
8. Fertig
```

## Module

### `face_tag_pipeline.py`
Hauptmodul, das alle Komponenten zusammenführt.

### `minio_client.py`
Client für minIO Objektspeicher (Upload/Download von Bildern).

### `face_detection.py`
Integration mit Face Detection Service (MLX-optimiert).

### `embeddings.py`
Integration mit Embedding Service (ArcFace/MLX).

### `clustering.py`
DBSCAN-Clustering für Gesichts-Gruppierung.

### `llm_service.py`
Integration mit LLM Service (GPT-OSS-120B/MLX-LM) für Annotationen.

### `neo4j_client.py`
Client für Neo4j Graph-Datenbank.

### `cli.py`
Command-Line Interface für Pipeline-Ausführung.

## Error Handling

Die Pipeline enthält umfassendes Error Handling:

- **Retry-Mechanismen** für Service-Calls
- **Exponential Backoff** bei Fehlern
- **Detailliertes Logging** aller Schritte
- **Fehler-Reporting** im Ergebnis-Dictionary

## Logging

Logs werden standardmäßig in `pipeline.log` geschrieben. Das Log-Level kann in `config.yaml` konfiguriert werden:

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "pipeline.log"
```

## Performance

Die Pipeline ist für Batch-Processing optimiert:

- **Batch-Embeddings** für effiziente Verarbeitung
- **Parallele Service-Calls** wo möglich
- **MLX-Optimierung** für Apple Silicon

## Beispiel-Output

```json
{
  "photo_id": "550e8400-e29b-41d4-a716-446655440000",
  "image_path": "/path/to/image.jpg",
  "timestamp": "2024-01-15T10:30:00",
  "faces": [
    {
      "box": [100, 150, 200, 250],
      "confidence": 0.95,
      "embedding": [0.123, 0.456, ...],
      "cluster_id": 0,
      "crop_path": "crops/photo_id_face_0.jpg"
    }
  ],
  "clusters": [
    {
      "cluster_id": 0,
      "name": "Max Mustermann",
      "n_faces": 3,
      "event_info": {
        "date": "1980er",
        "event_type": "Geburtstag",
        "location": null
      }
    }
  ],
  "errors": []
}
```

## Voraussetzungen

- **Face Detection Service** muss auf Port 5001 laufen
- **Embedding Service** muss auf Port 5002 laufen
- **LLM Service** muss auf Port 8000 laufen (ChatGPT-kompatible API)
- **minIO** muss auf Port 9000 laufen
- **Neo4j** muss auf Port 7687 laufen

## Troubleshooting

### Service nicht erreichbar
- Prüfe, ob alle Services laufen
- Prüfe die URLs in `config.yaml`
- Prüfe Firewall/Netzwerk-Einstellungen

### Neo4j-Verbindungsfehler
- Prüfe Credentials in `config.yaml`
- Prüfe, ob Neo4j läuft: `neo4j status`

### minIO-Fehler
- Prüfe Endpoint und Credentials
- Stelle sicher, dass Buckets existieren (werden automatisch erstellt)

### LLM-Timeout
- Erhöhe `timeout` in `config.yaml` für LLM-Service
- Prüfe, ob das Modell geladen ist

## Weitere Informationen

Siehe auch:
- [Face Tagging Software Dokumentation](../face_tag_software.md)
- [MLX Model Loading](../MLX_MODEL_LOADING.md)
- [exo Framework](../exo/)


