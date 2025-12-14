# Admin Dashboard - Mac Studio Cluster

Web-basiertes Admin-Interface für Installation, Konfiguration und Verwaltung des Mac Studio Clusters.

## 🚀 Schnellstart

```bash
cd admin
./start_admin.sh
```

Dann öffne im Browser: http://localhost:8080

## 📋 Features

### Übersicht
- Cluster-Status (Nodes, CPUs, GPUs)
- Service-Status (Face Detection, Embedding, LLM, minIO, Neo4j)
- System-Informationen (RAM, Disk)

### Installation
- Automatische Installation aller Dependencies
- Virtual Environment Setup
- exo Framework Installation
- Live-Log-Output

### Services
- Services starten/stoppen
- Service-Status prüfen
- Alle Services auf einmal verwalten

### VLAN Setup
- VLAN-Konfiguration für Head/Worker/Storage Nodes
- IP-Adressen konfigurieren
- Live-Log-Output

### Konfiguration
- Pipeline-Konfiguration anpassen
- Service-Endpoints konfigurieren
- minIO und Neo4j Einstellungen

### Status
- Detaillierter Cluster-Status
- Service-Health-Checks
- System-Ressourcen

## 🔧 Installation

### Dependencies

```bash
source mlx_env/bin/activate
pip install flask flask-cors psutil
```

### Start

```bash
./start_admin.sh
```

Oder manuell:

```bash
source mlx_env/bin/activate
cd admin
python3 admin_server.py
```

## 🌐 API Endpoints

### Status
- `GET /api/status` - Cluster- und Service-Status
- `GET /api/services/status` - Service-Status

### Installation
- `POST /api/install` - Startet Installation (Streaming)

### Services
- `POST /api/services/<service>/start` - Startet Service
- `POST /api/services/<service>/stop` - Stoppt Service

### VLAN
- `POST /api/vlan/setup` - VLAN Setup (Streaming)

### Konfiguration
- `GET /api/config/<type>` - Lädt Konfiguration
- `POST /api/config/<type>` - Speichert Konfiguration

## 🎨 Interface

Das Dashboard bietet eine moderne, benutzerfreundliche Oberfläche mit:

- **Tabs** für verschiedene Bereiche
- **Live-Updates** für Status-Informationen
- **Streaming-Logs** für Installation und Setup
- **Responsive Design** für verschiedene Bildschirmgrößen

## 🔒 Sicherheit

**Wichtig:** Das Admin-Dashboard läuft standardmäßig auf allen Interfaces (0.0.0.0).

Für Produktion:
- Nutze einen Reverse Proxy (nginx)
- Aktiviere HTTPS
- Implementiere Authentifizierung
- Beschränke Zugriff auf lokales Netzwerk

## 🐛 Troubleshooting

### Port bereits belegt

```bash
# Anderen Port verwenden
PORT=8081 python3 admin_server.py
```

### Dependencies fehlen

```bash
source mlx_env/bin/activate
pip install flask flask-cors psutil
```

### Services nicht erreichbar

- Prüfe ob Services laufen
- Prüfe Firewall-Einstellungen
- Prüfe Service-Konfiguration

## 📚 Weitere Informationen

- [Haupt-README](../README.md)
- [Installation Guide](../INSTALLATION.md)
- [VLAN Setup](../VLAN_SETUP.md)
