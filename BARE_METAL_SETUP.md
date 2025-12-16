# Bare Metal Setup - Face Tagging System

Diese Anleitung beschreibt, wie das Face Tagging System **ohne Docker** auf bare metal läuft.

## Übersicht

Das System läuft nativ auf macOS ohne Containerisierung. Alle Services werden direkt auf dem Host-System ausgeführt.

## Services

### 1. Face Detection Service (Port 5001)
```bash
./services/start_services.sh
```
Startet automatisch den Face Detection Service.

### 2. Embedding Service (Port 5002)
Wird automatisch mit `start_services.sh` gestartet.

### 3. LLM Service - exo (Port 8000)
Wird automatisch gestartet, falls `exo/` Verzeichnis vorhanden ist.

### 4. Streamlit App (Port 8501)
```bash
streamlit run streamlit_app/app.py --server.port 8501
```

### 5. Admin Server (Port 8080)
```bash
python admin/admin_server.py
```

## Start aller Services

```bash
# Services starten
./services/start_services.sh

# Streamlit App starten
streamlit run streamlit_app/app.py --server.port 8501

# Admin Server starten (optional)
python admin/admin_server.py
```

## Services stoppen

```bash
# Alle Services stoppen
./services/stop_services.sh

# Streamlit stoppen
kill $(lsof -ti :8501)

# Admin Server stoppen
kill $(lsof -ti :8080)
```

## Voraussetzungen

- Python 3.10+ (empfohlen: 3.12)
- Virtual Environment: `mlx_env/`
- Alle Dependencies installiert: `pip install -e .`

## Docker (Optional)

Das `docker/` Verzeichnis enthält eine optionale Docker-Containerisierung. Diese wird **nicht** für den normalen Betrieb benötigt.

Falls Docker verwendet werden soll, siehe `docker/README.md`.

## Troubleshooting

### Port bereits belegt
```bash
# Prüfe welcher Prozess den Port verwendet
lsof -i :5001

# Beende den Prozess
kill $(lsof -ti :5001)
```

### Services starten nicht
```bash
# Prüfe Logs
tail -f services/face_detection.log
tail -f services/embedding.log
tail -f services/exo.log
```

### Virtual Environment nicht aktiviert
```bash
source mlx_env/bin/activate
```

