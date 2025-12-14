# Face Tagging Services

Services für die Face Tagging Pipeline, optimiert für MLX auf Apple Silicon.

## Services

### 1. Face Detection Service (Port 5001)
- **Endpoint:** `http://localhost:5001`
- **Health Check:** `http://localhost:5001/health`
- **Detect:** `POST http://localhost:5001/detect`

### 2. Embedding Service (Port 5002)
- **Endpoint:** `http://localhost:5002`
- **Health Check:** `http://localhost:5002/health`
- **Embed:** `POST http://localhost:5002/embed`
- **Batch Embed:** `POST http://localhost:5002/embed/batch`

### 3. LLM Service (exo) (Port 8000)
- **Endpoint:** `http://localhost:8000`
- **Models:** `http://localhost:8000/v1/models`
- **Chat Completions:** `POST http://localhost:8000/v1/chat/completions`

## Start/Stop

### Services starten

```bash
cd /Users/blaubaer/Documents/Aphrodite/MacStudioCluster
./services/start_services.sh
```

Das Script:
- Aktiviert automatisch `mlx_env`
- Installiert benötigte Dependencies
- Startet alle Services im Hintergrund
- Führt Health Checks durch

### Services stoppen

```bash
./services/stop_services.sh
```

## Service-Status prüfen

```bash
# Face Detection
curl http://localhost:5001/health

# Embedding
curl http://localhost:5002/health

# LLM (exo)
curl http://localhost:8000/v1/models
```

## Logs

Logs werden in `services/` gespeichert:
- `face_detection.log` - Face Detection Service
- `embedding.log` - Embedding Service
- `exo.log` - LLM Service (exo)

## API-Beispiele

### Face Detection

```bash
# Bild als Base64 kodieren
IMAGE_B64=$(base64 -i /path/to/image.jpg)

curl -X POST http://localhost:5001/detect \
  -H "Content-Type: application/json" \
  -d "{
    \"image\": \"$IMAGE_B64\",
    \"return_landmarks\": true,
    \"return_confidence\": true
  }"
```

### Embedding

```bash
# Gesichts-Crop als Base64 kodieren
CROP_B64=$(base64 -i /path/to/face_crop.jpg)

curl -X POST http://localhost:5002/embed \
  -H "Content-Type: application/json" \
  -d "{
    \"image\": \"$CROP_B64\",
    \"normalize\": true
  }"
```

### LLM (exo)

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.2-3b",
    "messages": [{"role": "user", "content": "Hallo!"}],
    "temperature": 0.7
  }'
```

## Hinweise

- **MLX Models:** Die Services verwenden aktuell Fallback-Implementierungen. Echte MLX-Modelle müssen noch integriert werden.
- **Ports:** Stelle sicher, dass die Ports 5001, 5002 und 8000 frei sind.
- **mlx_env:** Die Services laufen im `mlx_env` Virtual Environment.

## Troubleshooting

### Port bereits belegt
```bash
# Prüfe welche Prozesse die Ports verwenden
lsof -i :5001
lsof -i :5002
lsof -i :8000

# Oder stoppe alle Services
./services/stop_services.sh
```

### Service startet nicht
- Prüfe die Logs in `services/*.log`
- Stelle sicher, dass `mlx_env` existiert und aktiviert ist
- Prüfe, ob alle Dependencies installiert sind

### Health Check schlägt fehl
- Warte ein paar Sekunden nach dem Start
- Prüfe die Logs auf Fehlermeldungen
- Stelle sicher, dass Flask installiert ist: `pip install flask`
