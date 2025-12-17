# exo Installation & Verwendung

[exo](https://github.com/exo-explore/exo) ist erfolgreich installiert!

## Was ist exo?

exo ist ein Framework, um AI-Cluster mit alltäglichen Geräten zu betreiben. Es ermöglicht verteilte Inference über mehrere Geräte hinweg, unterstützt MLX für Apple Silicon und kann große Modelle über mehrere Geräte verteilen.

## Installation

exo wurde mit **Python 3.12** installiert (empfohlene Version) in einem eigenen virtuellen Environment:

```bash
cd exo
source .venv/bin/activate
```

## Verwendung

### Einfacher Start

```bash
# Environment aktivieren
cd exo
source .venv/bin/activate

# exo starten
exo
```

exo startet automatisch:
- **WebUI** auf `http://localhost:<chatgpt-api-port>`
- **ChatGPT-kompatible API** auf `http://localhost:<chatgpt-api-port>/v1/chat/completions`

Hinweis: Der Port ist konfigurierbar über `--chatgpt-api-port`.
In diesem Projekt wird exo typischerweise mit Port `8000` gestartet (siehe `services/start_services.sh`).

### Modelle ausführen

#### Einzelnes Modell auf einem Gerät:

```bash
exo run llama-3.2-3b
```

#### Mit Custom Prompt:

```bash
exo run llama-3.2-3b --prompt "Was ist exo?"
```

### Multi-Device Setup

**Device 1:**
```bash
exo
```

**Device 2:**
```bash
exo
```

exo entdeckt automatisch andere Geräte im Netzwerk - keine Konfiguration nötig!

### API-Beispiele

#### Llama 3.2 3B:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
     "model": "llama-3.2-3b",
     "messages": [{"role": "user", "content": "Was ist exo?"}],
     "temperature": 0.7
   }'
```

#### Llama 3.1 405B (verteilt über mehrere Geräte):

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
     "model": "llama-3.1-405b",
     "messages": [{"role": "user", "content": "Was ist exo?"}],
     "temperature": 0.7
   }'
```

## Features

- **Automatische Device-Discovery** - Keine manuelle Konfiguration
- **MLX Support** - Native Apple Silicon Optimierung
- **tinygrad Support** - Cross-Platform Inference
- **ChatGPT-kompatible API** - Einfache Integration
- **P2P-Architektur** - Keine Master-Worker-Hierarchie
- **Heterogene Geräte** - Verschiedene Hardware-Kapazitäten

## Model Storage

Modelle werden standardmäßig in `~/.cache/exo/downloads` gespeichert.

Anderen Speicherort setzen:
```bash
export EXO_HOME=/path/to/models
exo
```

## Modelle laden (Download, Cache, Offline)

### Kurzfassung

- **Ein Modell wird geladen, sobald du es das erste Mal verwendest** (Download von Hugging Face in den Cache).
- Standard-Cache: `~/.cache/exo/downloads/` (änderbar via `EXO_HOME`).
- Du kannst Modelle **ohne Registrierung** direkt per Hugging-Face-Repo-ID verwenden oder sie **dauerhaft** in `exo/exo/models.py` registrieren.

### Variante A: Automatisch beim ersten Aufruf (empfohlen)

1) exo starten (in diesem Projekt üblicherweise Port 8000):

```bash
cd exo
source .venv/bin/activate
exo --chatgpt-api-port 8000 --disable-tui
```

2) Modell verwenden (exo lädt es bei Bedarf automatisch):

```bash
exo run llama-3.2-3b
```

oder über die API:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.2-3b",
    "messages": [{"role": "user", "content": "Hallo"}],
    "temperature": 0.7
  }'
```

### Variante B: Direkt per Hugging-Face-Repo-ID (ohne Registrierung)

```bash
exo run mlx-community/Llama-3.2-3B-Instruct-4bit
```

oder per API:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mlx-community/Llama-3.2-3B-Instruct-4bit",
    "messages": [{"role": "user", "content": "Hallo"}]
  }'
```

### Variante C: Modelle vorab herunterladen (Offline/Proxy)

Modelle liegen nach dem Download im Cache, z.B.:

```bash
ls ~/.cache/exo/downloads
```

Wenn du manuell herunterladen willst (z.B. wegen restriktivem Netzwerk), nutze `huggingface-cli`:

```bash
pip install huggingface_hub
huggingface-cli download mlx-community/Llama-3.2-3B-Instruct-4bit \
  --local-dir ~/.cache/exo/downloads/mlx-community--Llama-3.2-3B-Instruct-4bit
```

Falls du einen Mirror/Proxy nutzen musst:

```bash
HF_ENDPOINT=https://hf-mirror.com exo --chatgpt-api-port 8000 --disable-tui
```

Private Repos: Token setzen (Beispiel):

```bash
export HUGGINGFACE_HUB_TOKEN="..."
```

### Variante D: Modelle "seeden" (vorgefülltes Modell-Verzeichnis)

exo unterstützt das Vorladen/Seeden über `--models-seed-dir` (z.B. wenn du Modelle bereits auf ein NAS oder einen USB-Datenträger kopiert hast):

```bash
exo --models-seed-dir /pfad/zu/deinen/modellen --chatgpt-api-port 8000 --disable-tui
```

### Prüfen, ob ein Modell verfügbar ist

Liste der verfügbaren Modelle (API):

```bash
curl http://localhost:8000/v1/models
```

Debug-Logs (hilfreich bei Download-/Cache-Problemen):

```bash
DEBUG=9 exo --chatgpt-api-port 8000 --disable-tui
```

## Debugging

Debug-Logs aktivieren:
```bash
DEBUG=9 exo
```

Für tinygrad-spezifische Debug-Logs:
```bash
TINYGRAD_DEBUG=2 exo
```

## MLX Optimierung

Für optimale Performance auf Apple Silicon:

```bash
cd exo
./configure_mlx.sh
```

Dies optimiert die GPU-Memory-Allokation auf Apple Silicon Macs.

## Integration mit Face Tagging Projekt

exo kann als LLM-Service für das Face Tagging Projekt verwendet werden:

- **Alternative zu GPT-OSS-120B:** Nutze exo für lokale LLM-Inference
- **Multi-Device:** Verteile große Modelle über mehrere Mac Studio Nodes
- **ChatGPT-API:** Einfache Integration in bestehende Backend-Services

## Modelle hinzufügen

Siehe ausführliche Anleitung in `MODELLE_HINZUFUEGEN.md`

**Kurzfassung:**
1. Bearbeite `exo/exo/models.py`
2. Füge Modell zum `model_cards` Dictionary hinzu
3. Teste mit `exo run modell-name`

**Hilfs-Script:**
```bash
cd exo
source .venv/bin/activate
python add_model_example.py
```

## Weitere Informationen

- GitHub: https://github.com/exo-explore/exo
- Dokumentation: Siehe README.md im exo-Verzeichnis
- Modelle hinzufügen: Siehe MODELLE_HINZUFUEGEN.md

