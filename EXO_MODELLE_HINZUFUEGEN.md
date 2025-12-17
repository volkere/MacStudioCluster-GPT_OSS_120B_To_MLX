# Modelle zu exo hinzufügen

Diese Anleitung erklärt, wie du neue Modelle zu exo hinzufügen kannst.

Hinweis: Im Haupt-Repository ist `exo/` als Git-Submodule eingebunden. Diese Datei ist deshalb als referenzierbare, versionierte Kopie im Haupt-Repository abgelegt.

## Übersicht

Modelle in exo werden in `exo/exo/models.py` definiert. Es gibt mehrere Möglichkeiten, Modelle hinzuzufügen:

1. **Neue Modelle in models.py registrieren** (für permanente Integration)
2. **Modelle direkt über Hugging Face Repository-ID verwenden** (ohne Registrierung)
3. **Lokale Modelle verwenden** (manuell heruntergeladen)

---

## Methode 1: Modelle in models.py registrieren

### Schritt 1: Modell-Informationen sammeln

Du brauchst:
- **Modellname** (z.B. `"mein-modell-7b"`)
- **Anzahl der Layers** (aus der config.json des Modells)
- **Hugging Face Repository-ID** (z.B. `"mlx-community/Llama-3.2-3B-Instruct-4bit"`)

### Schritt 2: models.py bearbeiten

Öffne `exo/exo/models.py` und füge dein Modell zum `model_cards` Dictionary hinzu:

```python
model_cards = {
  # ... bestehende Modelle ...
  
  "mein-modell-7b": {
    "layers": 32,  # Anzahl der Transformer-Layers
    "repo": {
      "MLXDynamicShardInferenceEngine": "mlx-community/Mein-Modell-7B-4bit",
      # Optional: "TinygradDynamicShardInferenceEngine": "huggingface/Mein-Modell-7B",
    },
  },
}
```

### Schritt 3: Pretty Name hinzufügen (optional)

Füge einen lesbaren Namen zum `pretty_name` Dictionary hinzu:

```python
pretty_name = {
  # ... bestehende Namen ...
  "mein-modell-7b": "Mein Modell 7B",
}
```

### Schritt 4: Anzahl der Layers ermitteln

Die Anzahl der Layers findest du in der `config.json` des Modells:

```bash
# Beispiel: Modell von Hugging Face herunterladen und prüfen
cd ~/.cache/exo/downloads
# Oder direkt von Hugging Face:
curl https://huggingface.co/mlx-community/Llama-3.2-3B-Instruct-4bit/raw/main/config.json | grep num_hidden_layers
```

Oder verwende Python:

```python
import json
from pathlib import Path

# Wenn Modell bereits heruntergeladen
config_path = Path("~/.cache/exo/downloads/mlx-community--Llama-3.2-3B-Instruct-4bit/config.json")
with open(config_path.expanduser()) as f:
    config = json.load(f)
    print(f"Layers: {config.get('num_hidden_layers', config.get('num_layers', 'N/A'))}")
```

---

## Methode 2: Modelle direkt über Hugging Face Repository-ID verwenden

Du kannst Modelle auch direkt verwenden, ohne sie in `models.py` zu registrieren:

### Über die API:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
     "model": "mlx-community/Llama-3.2-3B-Instruct-4bit",
     "messages": [{"role": "user", "content": "Hallo!"}]
   }'
```

### Über exo run:

```bash
exo run mlx-community/Llama-3.2-3B-Instruct-4bit
```

**Hinweis:** Bei dieser Methode muss exo die Modell-Struktur automatisch erkennen können.

Hinweis zum Port: Wenn du exo mit einem anderen Port startest (z.B. `exo --chatgpt-api-port 52415`), passe die URL entsprechend an.

---

## Methode 3: Lokale Modelle verwenden

### Schritt 1: Modell manuell herunterladen

```bash
# Mit huggingface-cli
huggingface-cli download mlx-community/Llama-3.2-3B-Instruct-4bit \
  --local-dir ~/.cache/exo/downloads/mlx-community--Llama-3.2-3B-Instruct-4bit
```

Oder mit Python:

```python
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="mlx-community/Llama-3.2-3B-Instruct-4bit",
    local_dir="~/.cache/exo/downloads/mlx-community--Llama-3.2-3B-Instruct-4bit"
)
```

### Schritt 2: Modell in models.py registrieren

Füge das lokale Modell hinzu:

```python
"mein-lokales-modell": {
  "layers": 32,
  "repo": {
    "MLXDynamicShardInferenceEngine": "mlx-community--Llama-3.2-3B-Instruct-4bit",  # Lokaler Pfad
  },
}
```

---

## Modell-Struktur Anforderungen

### Für MLX-Modelle:

Das Modell muss folgende Dateien enthalten:
- `config.json` - Modell-Konfiguration
- `tokenizer.json` oder `tokenizer_config.json` - Tokenizer
- `model*.safetensors` oder `weight*.safetensors` - Modell-Gewichte
- Optional: `model.safetensors.index.json` - Für große, shardierte Modelle

### Unterstützte Modell-Typen:

exo unterstützt verschiedene Modell-Architekturen:
- **Llama** (und kompatible wie Mistral)
- **Qwen**
- **Phi**
- **DeepSeek**
- **Gemma**
- **LLaVA** (Vision-Language)
- **Stable Diffusion**

Für neue Architekturen musst du möglicherweise einen neuen Modell-Loader in `exo/inference/mlx/models/` erstellen.

---

## Beispiel: Neues Modell hinzufügen

### Beispiel 1: Llama-kompatibles Modell

```python
# In exo/exo/models.py

model_cards = {
  # ... bestehende Modelle ...
  
  "mein-llama-modell-8b": {
    "layers": 32,  # Standard für 8B Llama-Modelle
    "repo": {
      "MLXDynamicShardInferenceEngine": "mlx-community/Mein-Llama-8B-4bit",
    },
  },
}

pretty_name = {
  # ... bestehende Namen ...
  "mein-llama-modell-8b": "Mein Llama Modell 8B",
}
```

### Beispiel 2: Qwen-Modell

```python
"mein-qwen-7b": {
  "layers": 28,  # Qwen 7B hat 28 Layers
  "repo": {
    "MLXDynamicShardInferenceEngine": "mlx-community/Qwen2.5-7B-Instruct-4bit",
  },
}
```

---

## Modell-Speicherort

### Standard-Speicherort:

```
~/.cache/exo/downloads/
```

### Anderen Speicherort setzen:

```bash
export EXO_HOME=/path/to/your/models
exo
```

### Modell-Verzeichnis-Struktur:

```
~/.cache/exo/downloads/
├── mlx-community--Llama-3.2-3B-Instruct-4bit/
│   ├── config.json
│   ├── tokenizer.json
│   ├── model-00001-of-00002.safetensors
│   ├── model-00002-of-00002.safetensors
│   └── model.safetensors.index.json
```

---

## Modell testen

Nach dem Hinzufügen eines Modells:

```bash
# Environment aktivieren
cd exo
source .venv/bin/activate

# Modell testen
exo run mein-modell-7b

# Oder mit Prompt
exo run mein-modell-7b --prompt "Was ist exo?"
```

---

## Wichtige Hinweise

### 1. Layer-Anzahl

Die Layer-Anzahl ist kritisch für die korrekte Partitionierung über mehrere Geräte. Falsche Werte führen zu Fehlern.

### 2. MLX-kompatible Modelle

Für Apple Silicon sollten Modelle in MLX-Format vorliegen:
- 4-bit quantisiert: `-4bit` im Namen
- 8-bit quantisiert: `-8bit` im Namen
- BF16: `-bf16` im Namen

### 3. Hugging Face Repository

Das Modell muss auf Hugging Face verfügbar sein oder lokal vorhanden sein.

### 4. Modell-Konvertierung

Falls das Modell noch nicht in MLX-Format vorliegt, kannst du es konvertieren:

```python
from mlx_lm import convert

convert(
    hf_path="meta-llama/Llama-3.2-3B-Instruct",
    mlx_path="./mlx_models/llama-3.2-3b"
)
```

---

## Troubleshooting

### Problem: Modell wird nicht gefunden

**Lösung:**
- Prüfe, ob das Repository auf Hugging Face existiert
- Prüfe, ob der Modellname in `models.py` korrekt geschrieben ist
- Prüfe die Logs mit `DEBUG=9 exo`

### Problem: Falsche Layer-Anzahl

**Lösung:**
- Lade die `config.json` des Modells herunter
- Prüfe `num_hidden_layers` oder `num_layers`
- Aktualisiere den Wert in `models.py`

### Problem: Modell lädt nicht

**Lösung:**
- Prüfe, ob alle erforderlichen Dateien vorhanden sind
- Prüfe, ob das Modell-Format unterstützt wird
- Prüfe die exo-Logs für Fehlermeldungen

---

## Verfügbare MLX-Modelle auf Hugging Face

Beliebte MLX-kompatible Modelle:
- `mlx-community/*` - Offizielle MLX-konvertierte Modelle
- Suche nach `-4bit`, `-8bit`, `-mlx` in Modellnamen

**Beispiele:**
- `mlx-community/Llama-3.2-3B-Instruct-4bit`
- `mlx-community/Qwen2.5-7B-Instruct-4bit`
- `mlx-community/Phi-3.5-mini-instruct-4bit`

---

## Weitere Ressourcen

- [exo GitHub](https://github.com/exo-explore/exo)
- [MLX Model Conversion](https://github.com/ml-explore/mlx-examples)
- [Hugging Face MLX Models](https://huggingface.co/mlx-community)
