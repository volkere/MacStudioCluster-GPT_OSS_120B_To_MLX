# GPT-OSS-120B Verwendung

## Status

✅ **PyTorch installiert** - PyTorch 2.9.1 mit MPS (Metal Performance Shaders) Support für Apple Silicon
✅ **gpt-oss installiert** - Version 0.0.8
✅ **Modell heruntergeladen** - GPT-OSS-120B in `gpt-oss-120b/original/`

## Modell-Informationen

- **Layers:** 36 Transformer-Layers
- **Hidden Size:** 2880
- **Vocab Size:** 201088
- **MoE (Mixture of Experts):** 128 Experten, 4 pro Token
- **Context Length:** 4096 Tokens (erweiterbar auf 128k mit RoPE)

## Verwendung

### Option 1: Direkt mit gpt-oss

```bash
cd /Users/blaubaer/Documents/Aphrodite/MacStudioCluster
source mlx_env/bin/activate
python -m gpt_oss.chat gpt-oss-120b/original/
```

### Option 2: Als Python-Modul

```python
from gpt_oss.chat import ChatModel

# Modell laden
model = ChatModel("gpt-oss-120b/original/")

# Chat starten
model.chat()
```

### Option 3: Integration in Face Tagging Projekt

```python
from gpt_oss.chat import ChatModel
import json

# Modell initialisieren
gpt_model = ChatModel("gpt-oss-120b/original/")

def annotate_cluster(cluster_id, metadata):
    """Verwende GPT-OSS-120B für Cluster-Annotation"""
    prompt = f"""
    Analysiere folgenden Gesichts-Cluster:
    - Cluster ID: {cluster_id}
    - Metadaten: {json.dumps(metadata, indent=2)}
    
    Vorschlag für Person-Name und Kontext:
    """
    
    response = gpt_model.generate(prompt)
    return response

# Beispiel
annotation = annotate_cluster(
    cluster_id=17,
    metadata={
        "album": "Familienfotos 1975",
        "location_hint": "Wuppertal",
        "faces_in_cluster": 23
    }
)
print(annotation)
```

## Performance auf Apple Silicon

**Mit PyTorch MPS (Metal Performance Shaders):**
- Nutzt automatisch Apple GPU
- Unified Memory Architecture
- Erwartete Performance: ~5-10 tokens/s für 120B Modell

**Hinweis:** Für bessere Performance auf Apple Silicon sollte das Modell zu MLX konvertiert werden (siehe unten).

## MLX-Konvertierung (Empfohlen für Apple Silicon)

Für optimale Performance auf Apple Silicon:

### Schritt 1: Modell zu MLX konvertieren

```python
from mlx_lm import convert

# Konvertiere GPT-OSS-120B zu MLX
convert(
    hf_path="gpt-oss-120b/original/",
    mlx_path="./mlx_models/gpt-oss-120b-4bit",
    quantize=True,  # 4-bit Quantisierung
    q_group_size=64
)
```

### Schritt 2: Mit MLX-LM verwenden

```python
from mlx_lm import load, generate

# MLX-Modell laden
model, tokenizer = load("./mlx_models/gpt-oss-120b-4bit")

# Inference
prompt = "Analysiere diesen Gesichts-Cluster..."
response = generate(model, tokenizer, prompt=prompt, max_tokens=500)
print(response)
```

### Schritt 3: In exo integrieren

Füge GPT-OSS-120B zu exo hinzu:

```python
# In exo/exo/models.py
"gpt-oss-120b": {
  "layers": 36,
  "repo": {
    "MLXDynamicShardInferenceEngine": "./mlx_models/gpt-oss-120b-4bit",
  },
}
```

Dann verwenden:
```bash
exo run gpt-oss-120b
```

## Speicher-Anforderungen

**PyTorch (Original):**
- ~240 GB RAM für 120B Modell (FP16)
- Mit Quantisierung: ~60-120 GB

**MLX (Quantisiert):**
- 4-bit: ~60 GB
- 8-bit: ~120 GB

**Empfehlung:** Für Mac Studio mit 128GB+ RAM ist das Modell gut nutzbar.

## Troubleshooting

### Problem: "Out of Memory"

**Lösung:**
- Verwende quantisierte Version (4-bit/8-bit)
- Reduziere Batch-Size
- Nutze MLX statt PyTorch

### Problem: "MPS not available"

**Lösung:**
```python
import torch
print(torch.backends.mps.is_available())  # Sollte True sein
```

Falls False:
- macOS 12.3+ erforderlich
- Metal Framework muss verfügbar sein

### Problem: Langsame Performance

**Lösung:**
- Konvertiere zu MLX für 2-4x bessere Performance
- Nutze Quantisierung (4-bit)
- Verwende exo für Multi-Device-Verteilung

## Integration in Face Tagging Pipeline

```python
# face_tagging_pipeline.py
from gpt_oss.chat import ChatModel

class GPTOSSAnnotator:
    def __init__(self, model_path="gpt-oss-120b/original/"):
        self.model = ChatModel(model_path)
    
    def annotate_cluster(self, cluster_id, faces, metadata):
        """Generiere Annotation für einen Gesichts-Cluster"""
        prompt = self._build_annotation_prompt(cluster_id, faces, metadata)
        response = self.model.generate(prompt)
        return self._parse_response(response)
    
    def generate_cypher(self, annotation):
        """Generiere Neo4j Cypher-Statement"""
        prompt = f"""
        Generiere ein Neo4j Cypher-Statement für:
        {annotation}
        """
        cypher = self.model.generate(prompt)
        return cypher
    
    def _build_annotation_prompt(self, cluster_id, faces, metadata):
        return f"""
        Analysiere folgenden Gesichts-Cluster:
        
        Cluster ID: {cluster_id}
        Anzahl Gesichter: {len(faces)}
        Metadaten: {metadata}
        
        Vorschlag für:
        1. Person-Name (mit Confidence)
        2. Event/Ort-Kontext
        3. Zeitliche Einordnung
        
        Format: JSON
        """
```

## Weitere Ressourcen

- [GPT-OSS GitHub](https://github.com/openai/gpt-oss)
- [MLX-LM Dokumentation](https://github.com/ml-explore/mlx-examples/tree/main/lora)
- [exo Modelle hinzufügen](./exo/MODELLE_HINZUFUEGEN.md)

