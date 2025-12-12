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
- **WebUI** auf http://localhost:52415
- **ChatGPT-kompatible API** auf http://localhost:52415/v1/chat/completions

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
curl http://localhost:52415/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
     "model": "llama-3.2-3b",
     "messages": [{"role": "user", "content": "Was ist exo?"}],
     "temperature": 0.7
   }'
```

#### Llama 3.1 405B (verteilt über mehrere Geräte):

```bash
curl http://localhost:52415/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
     "model": "llama-3.1-405b",
     "messages": [{"role": "user", "content": "Was ist exo?"}],
     "temperature": 0.7
   }'
```

## Features

- ✅ **Automatische Device-Discovery** - Keine manuelle Konfiguration
- ✅ **MLX Support** - Native Apple Silicon Optimierung
- ✅ **tinygrad Support** - Cross-Platform Inference
- ✅ **ChatGPT-kompatible API** - Einfache Integration
- ✅ **P2P-Architektur** - Keine Master-Worker-Hierarchie
- ✅ **Heterogene Geräte** - Verschiedene Hardware-Kapazitäten

## Model Storage

Modelle werden standardmäßig in `~/.cache/exo/downloads` gespeichert.

Anderen Speicherort setzen:
```bash
export EXO_HOME=/path/to/models
exo
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

