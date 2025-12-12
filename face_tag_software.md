# Face Tag Software - Systemarchitektur

---

## Übersicht

Präsentation der Software-Architektur für ein Face-Tagging-System mit KI-gestützter Annotation und Graph-Datenbank

---

## 1. Eingangsquelle

### Input-Formate

- **Papierfoto** (Scan, Kameraaufnahme)
- **Digitales Foto**
- **Serienbilder / Kontaktabzüge**
- **Video-Frames**

### Ziel

Ein einheitliches Prozessformat, z. B. PNG/JPEG in einem "incoming"-Bucket in minIO.

---

## 2. Face Detection

Erster technischer Schritt nach dem Upload.

### Empfohlene Modelle

- **RetinaFace (InsightFace)** – sehr robust bei alten Fotos
- **DSFD** – hohe Genauigkeit
- **MTCNN** – etwas älter, aber schnell und zuverlässig

### Apple MLX Integration

**MLX (Machine Learning for Apple Silicon)** bietet optimierte Performance auf Mac Studio:

- **Native Apple Silicon Optimierung:** Direkte Nutzung der Neural Engine und GPU
- **Unified Memory:** Effiziente Speichernutzung ohne CPU-GPU-Transfer
- **Hohe Durchsatzrate:** 2-3x schneller als PyTorch/TensorFlow auf Apple Silicon
- **Energieeffizienz:** Geringerer Stromverbrauch bei gleicher Performance

**MLX-Implementierung für Face Detection:**
- RetinaFace-Modell konvertiert zu MLX-Format
- Batch-Processing mit MLX Arrays
- Automatische GPU/Neural Engine Nutzung

### Output pro Bild

```json
{
  "faces": [
    {
      "box": [x, y, w, h],
      "landmarks": {...}
    }
  ]
}
```

---

## 3. Embeddings erzeugen

Für Wiedererkennung / Clustering entscheidend.

### De-facto Standard

- **ArcFace / InsightFace** (beste Qualität)
- **DeepFace-Facenet512** (kompatibel, aber leicht schlechter)

### Apple MLX Integration

**MLX-optimierte Embedding-Generierung:**

- **ArcFace-MLX:** Konvertiertes ArcFace-Modell für MLX
- **Batch-Embedding:** Verarbeitung mehrerer Gesichter parallel
- **Vector-Operationen:** Optimierte Matrix-Multiplikation auf Apple Silicon
- **Performance:** ~0,1-0,2s pro Gesicht (vs. 0,3s mit PyTorch)

**Vorteile:**
- Schnellere Embedding-Generierung durch native Optimierung
- Geringerer Speicherverbrauch durch Unified Memory
- Bessere Skalierung bei Batch-Processing

### Output pro Gesicht

```json
{
  "embedding": [0.123, 0.543, ...],
  "confidence": 0.97
}
```

Diese Embeddings kommen in einen Vector Store oder werden in Neo4j oder minIO als JSON abgelegt.

---

## 4. Face-Clustering (unsupervised)

Optional, aber sehr hilfreich.

### Verfahren

- **HDBSCAN**
- **DBSCAN**
- **Agglomerative Clustering**

### Ziel

Ungeschilderte Gesichter gruppieren → "Person X taucht in 14 Bildern auf".

### Output

```json
{
  "cluster_id": 17,
  "faces_in_cluster": 23
}
```

---

## 5. GPT-OSS-120B für Annotation & Reasoning

Das ist der Gamechanger. Das Modell übernimmt die dynamische semantische Intelligenz.

### Apple MLX Integration für LLM-Inference

**MLX-optimierte LLM-Inference:**

- **MLX-LM:** Apple's optimiertes LLM-Framework für lokale Inference
- **Unified Memory Architecture:** Große Modelle (120B) können effizient auf Apple Silicon laufen
- **Quantisierung:** 4-bit/8-bit Quantisierung für reduzierte Speicheranforderungen
- **Performance:** 2-4x schneller als PyTorch-basierte Inference auf gleicher Hardware

**Alternative Modelle für MLX:**
- **Llama 3.1 70B/405B** (MLX-kompatibel)
- **Mistral 7B/8x7B** (MLX-kompatibel)
- **Phi-3** (MLX-kompatibel)
- **GPT-OSS-120B** (konvertiert zu MLX-Format)

**Vorteile MLX für LLM:**
- Lokale Inference ohne Cloud-Abhängigkeit
- Geringere Latenz durch native Optimierung
- Datenschutz: Daten bleiben lokal
- Kosteneinsparung: Keine Cloud-API-Kosten

### Was GPT-OSS-120B übernimmt

1. **Semantische Zuordnung der Cluster**
   - Beispiel: "Cluster 12 steht vermutlich für 'John Doe', weil die Metadaten des Albums auf 1975 verweisen und die gleiche Person in Beschriftungen vorkommt."

2. **Validierung von Fehlern**
   - "Diese drei Embeddings liegen weit auseinander → vermutlich fälschlich gemerged."
   - "Das Foto ist gespiegelt → Landmark-Muster verrät es."

3. **Kontextuelle Annotation**
   - Ort (aus Hintergrund, Metadaten, Textnotizen)
   - Ereignis (z. B. Tanztheater-Aufführung)
   - Zeitlogik (Reihenfolgen, Personen altern über die Jahre)

4. **Neo4j-Statements generieren**
   - Nodes für Person, Foto, Aufführung, Ort, Jahr
   - Relations wie APPEARS_IN, PERFORMED_AT, LOCATED_IN, NEXT_TO, SAME_PERSON

5. **Erstellung einer menschlich anpassbaren Annotations-Datei**

### Beispiel-Output: Cypher-Statements

```cypher
MERGE (p:Person {cluster_id: 17})
SET p.name = "vermutlich: Pina Bausch", p.confidence = 0.62

MATCH (f:Foto {id: "IMG_00123"})
MERGE (p)-[:APPEARS_IN {bbox: [x, y, w, h]}]->(f)
```

### Beispiel-Output: JSON-Annotations-Datei

```json
{
  "file": "IMG_00123",
  "timestamp": "ca. 1975",
  "location_hint": "Wuppertal Oper",
  "persons": [
    {
      "cluster": 17,
      "suggested_label": "Pina Bausch",
      "confidence": 0.62
    }
  ]
}
```

---

## 6. Speicherung (minIO + Neo4j)

### minIO

**Bucket-Struktur:**
- `incoming/` - Originale Bilder
- `processed/` - Verarbeitete Bilder
- `faces/` - Crops pro Gesicht
- `annotations/` - JSON mit Detektions- und Embedding-Daten

**Versionskontrolle:** z. B. nach Verbesserung der Modelle

### Neo4j

**Graph-Modell:**

**Nodes:**
- `:Foto`
- `:Person`
- `:Aufnahmeort`
- `:Aufführung`
- `:Cluster`
- `:Jahr` (optional)

**Relations:**
- `APPEARS_IN`
- `TAKEN_AT`
- `PART_OF`
- `LOCATED_IN`
- `SAME_AS` (zwischen Cluster und Person)
- `NEXT` (für Timeline)

### Neo4j - Cypher Beispiele

**Constraints & Indizes:**

```cypher
CREATE CONSTRAINT person_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.cluster_id IS UNIQUE;

CREATE CONSTRAINT foto_unique IF NOT EXISTS
FOR (f:Foto) REQUIRE f.id IS UNIQUE;

CREATE INDEX anno_timestamp IF NOT EXISTS
FOR (f:Foto) ON (f.timestamp);
```

**Basismodell einfügen:**

```cypher
MERGE (f:Foto {id: $foto_id})
ON CREATE SET f.path = $s3_path, f.timestamp = $timestamp, f.source = $source

MERGE (c:Cluster {id: $cluster_id})
SET c.size = coalesce(c.size, 0) + 1

MERGE (p:Person {cluster_id: $cluster_id})
ON CREATE SET p.suggested_labels = [$suggested_label], p.confidence = $confidence

MERGE (p)-[r:APPEARS_IN]->(f)
SET r.bbox = $bbox, r.confidence = $face_confidence

RETURN f, p, c, r
```

**Person mit Event verknüpfen:**

```cypher
MERGE (ev:Event {name: $event_name, year: $year})
MERGE (loc:Location {name: $location_name})
MERGE (ev)-[:LOCATED_IN]->(loc)
MERGE (p:Person {cluster_id: $cluster_id})
MERGE (p)-[:PERFORMED_AT {role: $role}]->(ev)
```

---

## 7. Timeline-Generierung

GPT-OSS-120B ist extrem gut darin, temporale Strukturen aus heterogenen Daten abzuleiten.

### Vorgehen

1. Extrahiere EXIF oder archivische Metadaten
2. GPT erhält:
   - Bildeindrücke
   - eventuelle Papier-Rückseiten-Notizen
   - Neo4j-Beziehungen
3. GPT schlägt eine wahrscheinliche Chronologie vor

### Output

```json
[
  {
    "date": "1977-02",
    "event": "Probe für Aufführung X",
    "photos": ["IMG_00123", "IMG_00124"]
  }
]
```

---

## 8. Streamlit-Frontend

Ziel: Nutzer kann kontrolliert durchsehen, korrigieren und exportieren.

### Typische Module

- **Foto-Viewer**
- **Face-Crop-Galerie**
- **Vorschläge des GPT-Modells**
- **Timeline-Viewer**
- **Neo4j-Graph-View**
- **CSV/JSON Export**

### Backend-APIs

Die Streamlit-App erwartet folgende Backend-APIs:

- `GET /pending` → Liste der ausstehenden Fotos mit Metadaten
- `GET /image/{foto_id}` → Originalbild
- `GET /face_crop/{foto_id}/{face_id}` → Gesichtscrop als Bild
- `POST /annotate` → Speichert menschliche Korrekturen (payload: foto_id, face_id, label, accepted)

---

## 9. Docker-Compose Architektur

### Services

- **Streamlit** - Frontend-Interface (Port 8501)
- **Backend** (FastAPI/Flask) - API-Layer (Port 8001)
- **minIO** - Objektspeicher (Ports 9000, 9001)
- **Neo4j** - Graph-Datenbank (Ports 7474, 7687)
- **Embedding-Service** (InsightFace/MLX) - Embedding-Generierung (Port 5002)
- **Face-Service** (MLX) - Face Detection (Port 5001)
- **MLX-LLM-Service** - LLM-Inference mit MLX (Port 8000)

### MLX-Services

**Face-Service (MLX):**
- RetinaFace-MLX für Face Detection
- Native Apple Silicon Optimierung
- Automatische GPU/Neural Engine Nutzung

**Embedding-Service (MLX):**
- ArcFace-MLX für Embedding-Generierung
- Batch-Processing optimiert
- Unified Memory Architecture

**MLX-LLM-Service:**
- MLX-LM für lokale LLM-Inference
- Unterstützt Llama, Mistral, Phi-3, GPT-OSS
- Quantisierte Modelle (4-bit/8-bit) für reduzierte Speicheranforderungen

### Features

- Healthchecks für alle Services
- Volumes für persistente Daten (minio_data, neo4j_data, gpt_models)
- Service-Dependencies definiert
- Umgebungsvariablen für Konfiguration

### Hinweise

- Ersetze die `ghcr.io/your-org/...` Images durch deine Builds oder offizielle Images
- Die gpt-oss Service-Definition ist ein Platzhalter: setze hier dein bevorzugtes Modell-Serving (z. B. vLLM, KServe, text-generation-webui)
- Speicheranforderungen für GPT-OSS-120B sind hoch; passe memory entsprechend an oder hoste das Modell auf spezialisierten Maschinen

---

## 10. Komplettes Ablaufdiagramm

```
Upload → minIO(incoming)
   ↓
Face Detection → Crops
   ↓
Embeddings → Clustering
   ↓
GPT-OSS-120B:
   - Cluster-Benennung
   - Event-/Ort-Anreicherung
   - Logik / Fehlerprüfung
   - Cypher-Generierung
   ↓
Neo4j: Speicherung der Graph-Struktur
   ↓
Timeline-Konstruktion via GPT
   ↓
Streamlit-UI: Review & Export
```

---

## Python Pipeline - Kernfunktionen

Modulare Komponenten für End-to-End Verarbeitung:

- `upload_to_minio()` - Upload zu Objektspeicher
- `detect_faces()` - Face Detection Service (MLX)
- `get_embedding()` - Embedding-Generierung (MLX)
- `cluster_embeddings()` - DBSCAN Clustering
- `ask_gpt_for_annotations()` - MLX-LLM Integration
- `generate_cypher_for_cluster()` - Cypher-Generierung
- `write_annotation_to_neo4j()` - Neo4j Persistierung
- `process_photo()` - End-to-End Flow für ein Foto

Die Pipeline verbindet alle Services und führt automatisch die komplette Verarbeitungskette aus: Upload → Detection → Embedding → Clustering → GPT-Annotation → Neo4j-Speicherung.

### MLX-Pipeline Beispiel

```python
import mlx.core as mx
import mlx.nn as nn
from mlx_face import RetinaFaceMLX
from mlx_embedding import ArcFaceMLX
from mlx_lm import load, generate

# Face Detection mit MLX
face_detector = RetinaFaceMLX()
faces = face_detector.detect(image)

# Embedding-Generierung mit MLX
embedding_model = ArcFaceMLX()
embeddings = embedding_model.encode(face_crops)

# LLM-Inference mit MLX
model, tokenizer = load("mlx_model")
response = generate(model, tokenizer, prompt=annotation_prompt)
```

---

## Technische Highlights

### KI-Integration

- **Face Detection:** RetinaFace (MLX), DSFD, MTCNN
- **Embeddings:** ArcFace/InsightFace (MLX-optimiert)
- **Clustering:** HDBSCAN, DBSCAN
- **Annotation:** GPT-OSS-120B / Llama 3.1 / Mistral (MLX-LM)

### Apple MLX Framework

- **Native Apple Silicon Optimierung:** Direkte Nutzung von GPU und Neural Engine
- **Unified Memory:** Effiziente Speichernutzung ohne CPU-GPU-Transfer
- **Performance:** 2-4x schneller als PyTorch/TensorFlow auf Apple Silicon
- **Energieeffizienz:** Geringerer Stromverbrauch bei gleicher Performance
- **Lokale Inference:** Keine Cloud-Abhängigkeit, vollständige Datenschutz-Kontrolle

### Datenbanken

- **minIO:** Objektspeicher für Bilder und Metadaten
- **Neo4j:** Graph-Datenbank für Beziehungen

### Frontend

- **Streamlit:** Interaktive UI für Review und Annotation

---

---

## 11. Apple MLX - Detaillierte Integration

### 11.1 MLX Installation & Setup

```bash
# MLX Installation
pip install mlx mlx-lm

# MLX Face Detection (custom package)
pip install mlx-face-detection

# MLX Embeddings (custom package)
pip install mlx-arcface
```

### 11.2 MLX Model Conversion

**Konvertierung bestehender Modelle zu MLX:**

```python
# PyTorch zu MLX Konvertierung
from mlx.utils import convert_weights

# RetinaFace PyTorch → MLX
retinaface_mlx = convert_weights(retinaface_pytorch)

# ArcFace PyTorch → MLX
arcface_mlx = convert_weights(arcface_pytorch)

# LLM Konvertierung (Llama, Mistral, etc.)
from mlx_lm import convert

convert("meta-llama/Llama-3.1-70B", mlx_path="./mlx_models/llama-3.1-70b")
```

### 11.3 MLX Performance-Benchmarks

**Erwartete Performance-Verbesserungen auf Mac Studio M3/M4:**

| Komponente | PyTorch/TensorFlow | MLX | Verbesserung |
|------------|-------------------|-----|--------------|
| Face Detection | 1,5s pro Bild | 0,5-0,8s | **~2x schneller** |
| Embedding (pro Gesicht) | 0,3s | 0,1-0,15s | **~2x schneller** |
| LLM Inference (70B) | 15-20 tokens/s | 30-40 tokens/s | **~2x schneller** |
| Energieverbrauch | 100% | 60-70% | **~30-40% weniger** |

### 11.4 MLX Memory Management

**Unified Memory Architecture Vorteile:**

- **Keine explizite GPU-Speicherverwaltung:** MLX nutzt automatisch Unified Memory
- **Große Modelle:** 120B Modelle können auf Mac Studio mit Unified Memory laufen
- **Effiziente Batch-Processing:** Mehrere Requests parallel ohne Speicher-Konflikte

**Speicher-Optimierung:**
```python
import mlx.core as mx

# Automatische Memory-Management
mx.set_default_device(mx.gpu)  # Nutzt GPU automatisch
mx.set_default_memory_limit(0.8)  # 80% des verfügbaren Speichers
```

### 11.5 MLX Service-Architektur

**MLX-basierte Microservices:**

```
Face-Service (MLX)
├── RetinaFace-MLX Model
├── Batch-Processing Queue
└── GPU/Neural Engine Auto-Detection

Embedding-Service (MLX)
├── ArcFace-MLX Model
├── Vector Normalization
└── Batch-Embedding Pipeline

MLX-LLM-Service
├── MLX-LM Framework
├── Quantized Models (4-bit/8-bit)
├── Prompt Template Engine
└── Streaming Response Support
```

### 11.6 MLX Quantisierung für LLMs

**Model Quantization für reduzierte Speicheranforderungen:**

```python
from mlx_lm import quantize

# 4-bit Quantisierung (75% Speicherreduktion)
quantize(
    model_path="./models/llama-3.1-70b",
    output_path="./models/llama-3.1-70b-4bit",
    bits=4
)

# 8-bit Quantisierung (50% Speicherreduktion)
quantize(
    model_path="./models/llama-3.1-70b",
    output_path="./models/llama-3.1-70b-8bit",
    bits=8
)
```

**Quantisierungs-Trade-offs:**
- **4-bit:** ~75% Speicherreduktion, ~5-10% Qualitätsverlust
- **8-bit:** ~50% Speicherreduktion, ~1-3% Qualitätsverlust
- **16-bit (FP16):** ~50% Speicherreduktion, minimaler Qualitätsverlust

### 11.7 MLX Deployment

**Docker-Container für MLX-Services:**

```dockerfile
# Dockerfile für MLX Face Service
FROM python:3.11-slim

# Apple Silicon Support
ENV PLATFORM=darwin-arm64

# MLX Installation
RUN pip install mlx mlx-face-detection

# Service Code
COPY face_service_mlx.py /app/
WORKDIR /app

CMD ["python", "face_service_mlx.py"]
```

**Native macOS Deployment (empfohlen):**
- MLX läuft am besten nativ auf macOS
- Docker kann für Isolation verwendet werden, aber native Performance ist optimal
- Empfehlung: Native Python-Umgebung mit MLX

### 11.8 MLX Code-Beispiele

**Face Detection Service mit MLX:**

```python
# face_service_mlx.py
import mlx.core as mx
import mlx.nn as nn
import numpy as np
from PIL import Image

class RetinaFaceMLX:
    def __init__(self, model_path="./models/retinaface_mlx"):
        # MLX Model laden
        self.model = self._load_mlx_model(model_path)
        mx.set_default_device(mx.gpu)  # GPU nutzen
        
    def detect(self, image: Image.Image) -> list:
        # Bild vorbereiten
        img_array = np.array(image.resize((640, 640)))
        img_tensor = mx.array(img_array.transpose(2, 0, 1))
        
        # Inference mit MLX
        with mx.stream():
            detections = self.model(img_tensor)
        
        # Ergebnisse verarbeiten
        faces = self._process_detections(detections)
        return faces
```

**Embedding Service mit MLX:**

```python
# embedding_service_mlx.py
import mlx.core as mx
import mlx.nn as nn
from mlx_arcface import ArcFaceMLX

class EmbeddingServiceMLX:
    def __init__(self):
        self.model = ArcFaceMLX()
        mx.set_default_device(mx.gpu)
        
    def encode_batch(self, face_crops: list) -> mx.array:
        # Batch-Processing für mehrere Gesichter
        batch = mx.array([self._preprocess(crop) for crop in face_crops])
        
        with mx.stream():
            embeddings = self.model.encode(batch)
        
        # Normalisierung
        embeddings = mx.linalg.normalize(embeddings, axis=1)
        return embeddings
```

**LLM Service mit MLX-LM:**

```python
# mlx_llm_service.py
from mlx_lm import load, generate
import mlx.core as mx

class MLXLLMService:
    def __init__(self, model_path="./mlx_models/llama-3.1-70b-4bit"):
        self.model, self.tokenizer = load(model_path)
        mx.set_default_memory_limit(0.8)  # 80% des Speichers
        
    def generate_annotation(self, prompt: str, max_tokens: int = 200) -> str:
        # Prompt vorbereiten
        full_prompt = f"""Du bist ein Assistent für Foto-Annotation.
Analysiere die folgenden Informationen und generiere strukturierte Annotationen.

{prompt}

Antwort (JSON-Format):"""
        
        # Generation mit MLX
        response = generate(
            self.model,
            self.tokenizer,
            prompt=full_prompt,
            max_tokens=max_tokens,
            temp=0.0,  # Deterministisch
            verbose=False
        )
        
        return response
```

### 11.9 MLX vs. PyTorch/TensorFlow Vergleich

| Aspekt | PyTorch/TensorFlow | MLX | Vorteil MLX |
|--------|-------------------|-----|-------------|
| **Performance (Apple Silicon)** | Baseline | 2-4x schneller | Ja |
| **Memory Management** | Manuell (CPU/GPU) | Unified Memory | Ja |
| **Energieverbrauch** | 100% | 60-70% | Ja |
| **Setup-Komplexität** | Mittel | Niedrig | Ja |
| **Model Availability** | Sehr groß | Wachsend | Teilweise |
| **Cross-Platform** | Ja | Nur Apple Silicon | Teilweise |
| **Community** | Sehr groß | Wachsend | Teilweise |

**Empfehlung:**
- **Für Apple Silicon:** MLX ist klar überlegen
- **Für Cross-Platform:** PyTorch/TensorFlow
- **Hybrid-Ansatz:** MLX für Apple Silicon, PyTorch als Fallback

### 11.10 MLX Best Practices

**1. Memory Management:**
```python
import mlx.core as mx

# Speicherlimit setzen
mx.set_default_memory_limit(0.8)  # 80% des verfügbaren Speichers

# Device-Auswahl
mx.set_default_device(mx.gpu)  # GPU bevorzugen
# mx.set_default_device(mx.cpu)  # CPU als Fallback
```

**2. Batch-Processing:**
```python
# Effizientes Batch-Processing
def process_batch(images: list, batch_size: int = 32):
    for i in range(0, len(images), batch_size):
        batch = images[i:i+batch_size]
        with mx.stream():
            results = model(batch)
        yield results
```

**3. Model Caching:**
```python
# Modelle im Speicher halten für wiederholte Inferenz
class ModelCache:
    def __init__(self):
        self.face_model = None
        self.embedding_model = None
        self.llm_model = None
        
    def get_face_model(self):
        if self.face_model is None:
            self.face_model = RetinaFaceMLX()
        return self.face_model
```

**4. Error Handling:**
```python
try:
    with mx.stream():
        result = model(input_data)
except mx.MemoryError:
    # Fallback auf CPU oder reduzierte Batch-Größe
    mx.set_default_device(mx.cpu)
    result = model(input_data)
```

### 11.11 MLX Pipeline Integration

**Vollständige MLX-Pipeline:**

```python
# pipeline_mlx.py
import mlx.core as mx
from face_service_mlx import RetinaFaceMLX
from embedding_service_mlx import EmbeddingServiceMLX
from mlx_llm_service import MLXLLMService
from sklearn.cluster import DBSCAN
import numpy as np

class MLXPipeline:
    def __init__(self):
        self.face_detector = RetinaFaceMLX()
        self.embedding_service = EmbeddingServiceMLX()
        self.llm_service = MLXLLMService()
        mx.set_default_device(mx.gpu)
        
    def process_photo(self, image_path: str):
        # 1. Face Detection
        faces = self.face_detector.detect(image_path)
        
        if not faces:
            return None
            
        # 2. Embedding-Generierung
        face_crops = [f['crop'] for f in faces]
        embeddings = self.embedding_service.encode_batch(face_crops)
        
        # 3. Clustering (numpy für sklearn)
        embeddings_np = np.array(embeddings)
        clusterer = DBSCAN(eps=0.6, min_samples=2, metric='cosine')
        cluster_labels = clusterer.fit_predict(embeddings_np)
        
        # 4. GPT-Annotation
        context = self._build_context(faces, cluster_labels)
        annotations = self.llm_service.generate_annotation(context)
        
        return {
            'faces': faces,
            'embeddings': embeddings,
            'clusters': cluster_labels,
            'annotations': annotations
        }
```

### 11.12 MLX Troubleshooting

**Häufige Probleme und Lösungen:**

**Problem 1: Out of Memory**
```python
# Lösung: Speicherlimit setzen oder Batch-Größe reduzieren
mx.set_default_memory_limit(0.7)  # Reduzieren auf 70%
# Oder: Kleinere Batches verarbeiten
```

**Problem 2: Model nicht kompatibel**
```python
# Lösung: Model konvertieren
from mlx.utils import convert_weights
converted_model = convert_weights(pytorch_model)
```

**Problem 3: Langsame Performance**
```python
# Lösung: Device prüfen und optimieren
print(mx.default_device())  # Sollte 'gpu' sein
mx.set_default_device(mx.gpu)  # Explizit GPU setzen
```

**Problem 4: Quantisierungsfehler**
```python
# Lösung: Verschiedene Quantisierungs-Level testen
# 8-bit ist stabiler als 4-bit
quantize(model_path, output_path, bits=8)
```

### 11.13 MLX Monitoring & Profiling

**Performance-Monitoring:**

```python
import mlx.core as mx
import time

class MLXProfiler:
    def __init__(self):
        self.timings = {}
        
    def profile(self, func, *args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        
        func_name = func.__name__
        if func_name not in self.timings:
            self.timings[func_name] = []
        self.timings[func_name].append(end - start)
        
        return result
    
    def get_stats(self):
        stats = {}
        for func_name, times in self.timings.items():
            stats[func_name] = {
                'mean': np.mean(times),
                'std': np.std(times),
                'min': np.min(times),
                'max': np.max(times)
            }
        return stats
```

**Memory-Usage Monitoring:**

```python
def get_memory_usage():
    """Gibt aktuelle MLX Memory-Nutzung zurück"""
    return {
        'allocated': mx.metal.get_memory_info()['allocated'],
        'cached': mx.metal.get_memory_info()['cached'],
        'total': mx.metal.get_memory_info()['total']
    }
```

### 11.14 MLX Model Repository

**Empfohlene MLX-kompatible Modelle:**

**Face Detection:**
- RetinaFace (konvertiert zu MLX)
- MTCNN (konvertiert zu MLX)
- DSFD (konvertiert zu MLX)

**Face Embeddings:**
- ArcFace (konvertiert zu MLX)
- InsightFace (konvertiert zu MLX)
- FaceNet (konvertiert zu MLX)

**LLMs (nativ MLX-kompatibel):**
- Llama 3.1 (70B, 405B)
- Mistral (7B, 8x7B)
- Phi-3 (3.8B, 14B)
- Qwen2.5 (verschiedene Größen)

**Model Download & Conversion:**

```bash
# MLX Models direkt herunterladen
python -m mlx_lm.convert \
    --hf-path meta-llama/Llama-3.1-70B \
    --mlx-path ./mlx_models/llama-3.1-70b

# Quantisierung
python -m mlx_lm.quantize \
    --model ./mlx_models/llama-3.1-70b \
    --bits 4 \
    --output ./mlx_models/llama-3.1-70b-4bit
```

### 11.15 MLX Deployment-Strategien

**Option 1: Native macOS (Empfohlen)**
```bash
# Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install mlx mlx-lm

# Service starten
python face_service_mlx.py
```

**Option 2: Docker (mit Einschränkungen)**
```dockerfile
# Dockerfile für Apple Silicon
FROM --platform=linux/arm64 python:3.11-slim

# MLX Installation (funktioniert nur auf ARM64)
RUN pip install mlx mlx-lm

# Service
COPY . /app
WORKDIR /app
CMD ["python", "service.py"]
```

**Option 3: Kubernetes (für Skalierung)**
- Native macOS Pods (mit Einschränkungen)
- Oder: Hybrid-Ansatz (MLX auf macOS, andere Services auf Linux)

### 11.16 MLX Performance-Tuning

**Optimierungstipps:**

1. **Batch-Größe optimieren:**
```python
# Teste verschiedene Batch-Größen
for batch_size in [8, 16, 32, 64]:
    throughput = test_throughput(batch_size)
    print(f"Batch {batch_size}: {throughput} FPS")
```

2. **Streaming für große Batches:**
```python
# Streaming für große Datenmengen
def process_stream(images, chunk_size=100):
    for chunk in chunks(images, chunk_size):
        with mx.stream():
            yield process_batch(chunk)
```

3. **Model Caching:**
```python
# Modelle im Speicher halten
@lru_cache(maxsize=1)
def get_model():
    return load_model()
```

4. **Parallel Processing:**
```python
# Mehrere Modelle parallel
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(process_image, image_batch)
```

---

## Ende

Vielen Dank für Ihre Aufmerksamkeit!

