# MacStudioCluster - GPT-OSS-120B to MLX

Dieses Repository enthält Tools und Anleitungen für die Konvertierung von GPT-OSS-120B zu MLX-Format für optimale Performance auf Apple Silicon.

## Projekt-Übersicht

- **Face Tagging System** mit MLX-Optimierung
- **GPT-OSS-120B Integration** für semantische Annotation
- **exo Framework** für verteilte AI-Inference
- **MLX-Monitoring Tools** für Performance-Tracking

## Projekt-Struktur

```
MacStudioCluster/
├── face_tag_software.md          # Software-Architektur Dokumentation
├── face_tag_hardware.md           # Hardware-Architektur Dokumentation
├── GPT_OSS_120B_ANLEITUNG.md     # GPT-OSS-120B Setup & Konvertierung
├── mlx_monitor.py                 # MLX Performance Monitoring Tool
├── exo/                           # exo Framework für verteilte Inference
│   ├── MODELLE_HINZUFUEGEN.md    # Anleitung: Modelle zu exo hinzufügen
│   └── add_model_example.py      # Script zum Hinzufügen von Modellen
├── gpt-oss-120b/                  # GPT-OSS-120B Modell (nur Config, keine Weights)
└── project_sizing_report.md      # Projekt-Sizing für 400k Fotos
```

## Quick Start

### 1. MLX Environment Setup

```bash
# Virtual Environment erstellen
python3 -m venv mlx_env
source mlx_env/bin/activate

# MLX installieren
pip install mlx mlx-lm
```

### 2. GPT-OSS-120B zu MLX konvertieren

```python
from mlx_lm import convert

convert(
    hf_path="gpt-oss-120b/original/",
    mlx_path="./mlx_models/gpt-oss-120b-4bit",
    quantize=True,
    q_group_size=64
)
```

### 3. MLX Monitoring

```bash
source mlx_env/bin/activate
python mlx_monitor.py
```

## Dokumentation

- **[GPT-OSS-120B Anleitung](./GPT_OSS_120B_ANLEITUNG.md)** - Vollständige Anleitung zur Konvertierung und Verwendung
- **[Face Tagging Software](./face_tag_software.md)** - Detaillierte Software-Architektur
- **[Face Tagging Hardware](./face_tag_hardware.md)** - Hardware-Architektur für Mac Studio Cluster
- **[exo Modelle hinzufügen](./exo/MODELLE_HINZUFUEGEN.md)** - Anleitung zum Hinzufügen von Modellen zu exo

## Features

### MLX-Optimierung
- Native Apple Silicon Performance
- Unified Memory Architecture
- 2-4x schneller als PyTorch
- Quantisierung (4-bit/8-bit)

### GPT-OSS-120B Integration
- PyTorch Support (MPS)
- MLX-Konvertierung
- exo-Integration für Multi-Device
- Face Tagging Pipeline Integration

### exo Framework
- Verteile AI-Inference über mehrere Geräte
- Automatische Device-Discovery
- ChatGPT-kompatible API
- MLX & tinygrad Support

## Performance

**MLX vs PyTorch auf Apple Silicon:**

| Komponente | PyTorch | MLX | Verbesserung |
|------------|---------|-----|--------------|
| Face Detection | 1.5s | 0.5-0.8s | **~2x** |
| Embedding | 0.3s | 0.1-0.15s | **~2x** |
| LLM Inference (70B) | 15-20 tok/s | 30-40 tok/s | **~2x** |

## Requirements

- **Python:** 3.10+
- **macOS:** 12.3+ (für MPS Support)
- **RAM:** 64GB+ empfohlen für GPT-OSS-120B
- **Hardware:** Apple Silicon (M1/M2/M3/M4)

## License

Siehe LICENSE Dateien in den jeweiligen Unterprojekten.

## Contributing

Beiträge sind willkommen! Bitte erstelle ein Issue oder Pull Request.

## Kontakt

Für Fragen oder Support, öffne bitte ein Issue auf GitHub.

---

**Hinweis:** Die Modell-Gewichte (`.safetensors` Dateien) sind nicht im Repository enthalten, da sie zu groß sind. Bitte lade sie separat von Hugging Face herunter.
