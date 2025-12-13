# LLM-Modelle von Hugging Face in Apple MLX laden

Diese Anleitung erklärt, wie du LLM-Modelle von Hugging Face in eine Apple MLX-Umgebung lädst und verwendest.

## Übersicht

Es gibt drei Hauptmethoden, um LLM-Modelle in MLX zu verwenden:

1. **Direktes Laden von MLX-konvertierten Modellen** (Empfohlen)
2. **Konvertierung von PyTorch/Transformers-Modellen zu MLX**
3. **Verwendung mit exo Framework** (für verteilte Inference)

---

## Methode 1: Direktes Laden von MLX-Modellen (Empfohlen)

### Schritt 1: MLX-kompatible Modelle finden

Die einfachste Methode ist, bereits konvertierte MLX-Modelle von Hugging Face zu verwenden:

**Beliebte MLX-Modelle:**
- `mlx-community/Llama-3.2-3B-Instruct-4bit`
- `mlx-community/Llama-3.1-70B-Instruct-4bit`
- `mlx-community/Qwen2.5-7B-Instruct-4bit`
- `mlx-community/Phi-3.5-mini-instruct-4bit`
- `mlx-community/Mistral-7B-Instruct-v0.2-4bit`

### Schritt 2: Modell mit mlx_lm laden

```python
from mlx_lm import load, generate

# Modell direkt von Hugging Face laden
model, tokenizer = load("mlx-community/Llama-3.2-3B-Instruct-4bit")

# Oder von lokalem Pfad
# model, tokenizer = load("./mlx_models/llama-3.2-3b-4bit")

# Text generieren
prompt = "Was ist Machine Learning?"
response = generate(model, tokenizer, prompt=prompt, max_tokens=500)
print(response)
```

### Schritt 3: Chat-Interface verwenden

```python
from mlx_lm import load
from mlx_lm.utils import generate_step

model, tokenizer = load("mlx-community/Llama-3.2-3B-Instruct-4bit")

# Chat-Template verwenden
messages = [
    {"role": "user", "content": "Erkläre mir MLX in einem Satz."}
]

prompt = tokenizer.apply_chat_template(
    messages, 
    tokenize=False, 
    add_generation_prompt=True
)

response = generate(model, tokenizer, prompt=prompt, max_tokens=200)
print(response)
```

---

## Methode 2: PyTorch/Transformers-Modelle zu MLX konvertieren

Falls ein Modell noch nicht in MLX-Format vorliegt, kannst du es konvertieren:

### Schritt 1: Modell von Hugging Face herunterladen

```python
from huggingface_hub import snapshot_download

# Modell herunterladen
snapshot_download(
    repo_id="meta-llama/Llama-3.2-3B-Instruct",
    local_dir="./models/llama-3.2-3b"
)
```

### Schritt 2: Zu MLX konvertieren

```python
from mlx_lm import convert

# Konvertierung ohne Quantisierung
convert(
    hf_path="meta-llama/Llama-3.2-3B-Instruct",
    mlx_path="./mlx_models/llama-3.2-3b"
)

# Oder direkt von lokalem Pfad
convert(
    hf_path="./models/llama-3.2-3b",
    mlx_path="./mlx_models/llama-3.2-3b"
)
```

### Schritt 3: Quantisierung (Optional, aber empfohlen)

Quantisierung reduziert den Speicherbedarf erheblich:

```python
from mlx_lm import convert, quantize

# Zuerst konvertieren
convert(
    hf_path="meta-llama/Llama-3.2-3B-Instruct",
    mlx_path="./mlx_models/llama-3.2-3b"
)

# Dann quantisieren (4-bit)
quantize(
    model_path="./mlx_models/llama-3.2-3b",
    output_path="./mlx_models/llama-3.2-3b-4bit",
    bits=4,
    group_size=64
)

# Oder in einem Schritt mit convert
convert(
    hf_path="meta-llama/Llama-3.2-3B-Instruct",
    mlx_path="./mlx_models/llama-3.2-3b-4bit",
    quantize=True,  # 4-bit Quantisierung
    q_group_size=64
)
```

### Schritt 4: Konvertiertes Modell laden

```python
from mlx_lm import load, generate

# Quantisiertes Modell laden
model, tokenizer = load("./mlx_models/llama-3.2-3b-4bit")

# Verwenden
response = generate(model, tokenizer, prompt="Hallo!", max_tokens=100)
print(response)
```

---

## Methode 3: Kommandozeilen-Tools

### Modell konvertieren (CLI)

```bash
# Mit Python-Modul
python -m mlx_lm.convert \
    --hf-path meta-llama/Llama-3.2-3B-Instruct \
    --mlx-path ./mlx_models/llama-3.2-3b

# Mit Quantisierung
python -m mlx_lm.convert \
    --hf-path meta-llama/Llama-3.2-3B-Instruct \
    --mlx-path ./mlx_models/llama-3.2-3b-4bit \
    --quantize \
    --q-bits 4 \
    --q-group-size 64
```

### Modell quantisieren (CLI)

```bash
python -m mlx_lm.quantize \
    --model ./mlx_models/llama-3.2-3b \
    --bits 4 \
    --output ./mlx_models/llama-3.2-3b-4bit \
    --group-size 64
```

### Modell direkt verwenden (CLI)

```bash
# Chat-Interface
python -m mlx_lm.chat --model mlx-community/Llama-3.2-3B-Instruct-4bit

# Text generieren
python -m mlx_lm.generate \
    --model mlx-community/Llama-3.2-3B-Instruct-4bit \
    --prompt "Was ist MLX?" \
    --max-tokens 200
```

---

## Erweiterte Verwendung

### Batch-Processing

```python
from mlx_lm import load, generate
import mlx.core as mx

model, tokenizer = load("mlx-community/Llama-3.2-3B-Instruct-4bit")

prompts = [
    "Was ist Machine Learning?",
    "Erkläre Neural Networks.",
    "Was ist Deep Learning?"
]

# Batch-Verarbeitung
for prompt in prompts:
    response = generate(
        model, 
        tokenizer, 
        prompt=prompt, 
        max_tokens=150,
        temp=0.7  # Temperature für Variation
    )
    print(f"Q: {prompt}\nA: {response}\n")
```

### Streaming-Output

```python
from mlx_lm import load
from mlx_lm.utils import generate_step

model, tokenizer = load("mlx-community/Llama-3.2-3B-Instruct-4bit")

prompt = "Erzähle eine kurze Geschichte über AI:"
prompt_tokens = tokenizer.encode(prompt)

# Streaming-Generierung
for token in generate_step(model, prompt_tokens, temp=0.7):
    token_str = tokenizer.decode([token])
    print(token_str, end="", flush=True)
print()  # Neue Zeile am Ende
```

### Custom Sampling-Parameter

```python
from mlx_lm import load, generate

model, tokenizer = load("mlx-community/Llama-3.2-3B-Instruct-4bit")

response = generate(
    model,
    tokenizer,
    prompt="Erkläre Quantum Computing:",
    max_tokens=300,
    temp=0.8,        # Temperature (höher = kreativer)
    top_p=0.9,       # Nucleus sampling
    top_k=50,        # Top-k sampling
    repetition_penalty=1.1  # Wiederholungsstrafe
)
print(response)
```

### Memory-Management für große Modelle

```python
import mlx.core as mx
from mlx_lm import load

# Memory-Limit setzen (80% des verfügbaren Speichers)
mx.set_default_memory_limit(0.8)

# Modell laden
model, tokenizer = load("mlx-community/Llama-3.1-70B-Instruct-4bit")

# Memory-Info abrufen
memory_info = mx.metal.get_memory_info()
print(f"Allocated: {memory_info['allocated'] / 1e9:.2f} GB")
print(f"Cached: {memory_info['cached'] / 1e9:.2f} GB")
```

---

## Integration mit exo Framework

Für verteilte Inference über mehrere Geräte:

### Schritt 1: Modell zu exo hinzufügen

Bearbeite `exo/exo/models.py`:

```python
model_cards = {
  "mein-llama-modell": {
    "layers": 28,  # Anzahl der Transformer-Layers
    "repo": {
      "MLXDynamicShardInferenceEngine": "mlx-community/Llama-3.2-3B-Instruct-4bit",
    },
  },
}
```

### Schritt 2: Mit exo verwenden

```bash
# Environment aktivieren
cd exo
source .venv/bin/activate

# Modell starten
exo run mein-llama-modell

# Oder direkt über Hugging Face Repository-ID
exo run mlx-community/Llama-3.2-3B-Instruct-4bit
```

### Schritt 3: API verwenden

```bash
curl http://localhost:52415/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
     "model": "mein-llama-modell",
     "messages": [{"role": "user", "content": "Hallo!"}],
     "temperature": 0.7
   }'
```

---

## Unterstützte Modell-Architekturen

MLX unterstützt folgende Architekturen:

- **Llama** (Llama 2, Llama 3, Llama 3.1, Llama 3.2)
- **Mistral** (Mistral 7B, Mixtral 8x7B)
- **Phi** (Phi-2, Phi-3, Phi-3.5)
- **Qwen** (Qwen 2, Qwen 2.5)
- **Gemma** (Gemma 2)
- **DeepSeek** (DeepSeek Coder, DeepSeek V2, DeepSeek R1)
- **Nemotron**
- **Stable Diffusion** (für Bildgenerierung)

---

## Quantisierungs-Optionen

### 4-bit Quantisierung (Empfohlen)

- **Speicher:** ~25% des Originalmodells
- **Performance:** Minimale Qualitätsverluste
- **Verwendung:** Für die meisten Anwendungen optimal

```python
convert(
    hf_path="meta-llama/Llama-3.2-3B-Instruct",
    mlx_path="./mlx_models/llama-3.2-3b-4bit",
    quantize=True,
    q_bits=4,
    q_group_size=64
)
```

### 8-bit Quantisierung

- **Speicher:** ~50% des Originalmodells
- **Performance:** Sehr geringe Qualitätsverluste
- **Verwendung:** Wenn 4-bit zu aggressiv ist

```python
convert(
    hf_path="meta-llama/Llama-3.2-3B-Instruct",
    mlx_path="./mlx_models/llama-3.2-3b-8bit",
    quantize=True,
    q_bits=8
)
```

### BF16 (Keine Quantisierung)

- **Speicher:** 100% des Originalmodells
- **Performance:** Beste Qualität
- **Verwendung:** Für kritische Anwendungen

```python
convert(
    hf_path="meta-llama/Llama-3.2-3B-Instruct",
    mlx_path="./mlx_models/llama-3.2-3b-bf16"
)
```

---

## Troubleshooting

### Problem: "Model not found"

**Lösung:**
- Prüfe, ob das Repository auf Hugging Face existiert
- Verwende die vollständige Repository-ID (z.B. `mlx-community/Llama-3.2-3B-Instruct-4bit`)
- Prüfe, ob du authentifiziert bist (für private Modelle)

### Problem: "Out of Memory"

**Lösung:**
- Verwende quantisierte Version (4-bit/8-bit)
- Reduziere Batch-Size
- Setze Memory-Limit: `mx.set_default_memory_limit(0.7)`
- Nutze exo für Multi-Device-Verteilung

### Problem: "Conversion failed"

**Lösung:**
- Prüfe, ob das Modell eine unterstützte Architektur hat
- Stelle sicher, dass alle Modell-Dateien vorhanden sind
- Prüfe die Logs für detaillierte Fehlermeldungen

### Problem: "Slow performance"

**Lösung:**
- Verwende quantisierte Modelle
- Nutze Unified Memory (automatisch auf Apple Silicon)
- Prüfe, ob Metal GPU aktiviert ist
- Nutze exo für Multi-Device-Verteilung

---

## Best Practices

1. **Verwende quantisierte Modelle:** 4-bit Quantisierung bietet beste Balance zwischen Qualität und Speicher
2. **Cache-Modelle lokal:** Lade Modelle einmal herunter und verwende lokale Pfade
3. **Memory-Management:** Setze Memory-Limits für große Modelle
4. **Batch-Processing:** Verarbeite mehrere Prompts gleichzeitig für bessere Effizienz
5. **Streaming:** Verwende Streaming für bessere User Experience bei langen Antworten

---

## Beispiel: Komplettes Setup

```python
#!/usr/bin/env python3
"""
Komplettes Beispiel: LLM-Modell in MLX laden und verwenden
"""

from mlx_lm import load, generate
import mlx.core as mx

# 1. Memory-Limit setzen
mx.set_default_memory_limit(0.8)

# 2. Modell laden (direkt von Hugging Face)
print("Lade Modell...")
model, tokenizer = load("mlx-community/Llama-3.2-3B-Instruct-4bit")

# 3. Chat-Interface
def chat(prompt, max_tokens=200, temp=0.7):
    """Einfaches Chat-Interface"""
    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=max_tokens,
        temp=temp
    )
    return response

# 4. Verwenden
if __name__ == "__main__":
    while True:
        user_input = input("\nDu: ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        response = chat(user_input)
        print(f"\nAI: {response}")
```

---

## Weitere Ressourcen

- [MLX-LM Dokumentation](https://github.com/ml-explore/mlx-examples/tree/main/lora)
- [MLX Community Models](https://huggingface.co/mlx-community)
- [exo Framework](https://github.com/exo-explore/exo)
- [MLX Examples](https://github.com/ml-explore/mlx-examples)

