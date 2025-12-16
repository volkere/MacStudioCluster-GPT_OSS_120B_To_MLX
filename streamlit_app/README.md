# Streamlit GUI für Face Tagging Pipeline

Benutzerfreundliche Web-GUI für die Verwaltung und Verarbeitung von Bildern.

## Features

- **Schritt-für-Schritt-Anleitung** - Klare Anweisungen für jeden Schritt
- **Bild-Upload** - Einfaches Hochladen von Bildern
- **Verarbeitungs-Status** - Live-Anzeige des Verarbeitungsfortschritts
- **Ergebnis-Visualisierung** - Übersichtliche Darstellung der Ergebnisse
- **Service-Status** - Prüfung ob alle Services laufen

## Installation

```bash
# Aktiviere Virtual Environment
source mlx_env/bin/activate

# Installiere Streamlit
pip install streamlit pillow requests
```

## Start

```bash
./streamlit_app/start_streamlit.sh
```

Oder manuell:

```bash
source mlx_env/bin/activate
cd /Users/blaubaer/Documents/Aphrodite/MacStudioCluster
streamlit run streamlit_app/app.py
```

## Zugriff

Nach dem Start öffne im Browser:
- **http://localhost:8501**

## Nutzung

### Schritt 1: Übersicht
- Prüfe Service-Status in der Sidebar
- Folge der Schritt-für-Schritt-Anleitung

### Schritt 2: Bild hochladen
- Gehe zur Seite "Bild hochladen"
- Wähle ein Bild aus (JPG, PNG, TIFF, BMP)
- Bild wird automatisch gespeichert

### Schritt 3: Verarbeitung
- Gehe zur Seite "Verarbeitung"
- Wähle Optionen (minIO Upload, Ray Cluster)
- Klicke auf "Verarbeitung starten"
- Warte auf Abschluss

### Schritt 4: Ergebnisse
- Gehe zur Seite "Ergebnisse"
- Sieh dir erkannte Gesichter an
- Prüfe Cluster und Annotationen
- Lade Ergebnis als JSON herunter

## Seiten

### 🏠 Übersicht
- Schritt-für-Schritt-Anleitung
- Service-Status
- Quick Actions

### 📤 Bild hochladen
- Datei-Upload
- Bild-Vorschau
- Bild-Informationen

### 🔄 Verarbeitung
- Verarbeitungs-Optionen
- Progress-Anzeige
- Zusammenfassung

### 📊 Ergebnisse
- Gesichter-Übersicht
- Cluster-Details
- JSON-Export

### ⚙️ Konfiguration
- Service-Endpoints
- minIO-Konfiguration
- Neo4j-Konfiguration

## Voraussetzungen

- Alle Services müssen laufen:
  - Face Detection (Port 5001)
  - Embedding (Port 5002)
  - LLM (Port 8000)
  - minIO (Port 9000)
  - Neo4j (Port 7687)

Starte Services mit:
```bash
./services/start_services.sh
```

## Troubleshooting

### Port bereits belegt
```bash
# Beende Prozess auf Port 8501
kill $(lsof -ti :8501)
```

### Services nicht erreichbar
- Prüfe ob Services laufen
- Prüfe URLs in `pipeline/config.yaml`
- Prüfe Firewall-Einstellungen

### Streamlit-Fehler
```bash
# Neu installieren
pip install --upgrade streamlit
```

## Weitere Informationen

- [Pipeline Dokumentation](../pipeline/README.md)
- [Pipeline Usage Guide](../PIPELINE_USAGE.md)
