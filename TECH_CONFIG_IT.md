# Technische Konfigurationsvorlage - Mac Studio Cluster
## Face Tagging System mit MLX und Ray

**Dokument:** Technische Konfiguration für IT-Management  
**Version:** 1.0  
**Datum:** 2024-12-14  
**Projekt:** Mac Studio Cluster - Face Tagging System

---

## 1. Übersicht

### 1.1 Projektbeschreibung
Distributed Face Tagging System für Mac Studio Cluster mit:
- MLX-optimierter Face Detection und Embedding-Generierung
- Ray-basierter verteilter Verarbeitung
- KI-gestützter Annotation (GPT-OSS-120B / Llama)
- Graph-Datenbank (Neo4j) für Beziehungen
- Monitoring mit Grafana und Prometheus

### 1.2 Architektur
- **Management Node:** Ray Head, LLM Service, Admin Dashboard, Monitoring
- **Worker Nodes:** Ray Workers, Face Detection, Embedding Services
- **Storage Node:** minIO Object Storage (optional)

---

## 2. Hardware-Anforderungen

### 2.1 Minimum-Spezifikationen

**Management Node:**
- **Hardware:** Mac Studio (M1/M2/M3/M4)
- **RAM:** 64GB (128GB empfohlen für GPT-OSS-120B)
- **Storage:** 1TB SSD (2TB empfohlen)
- **Netzwerk:** 10GbE empfohlen

**Worker Nodes:**
- **Hardware:** Mac Studio (M1/M2/M3/M4)
- **RAM:** 64GB
- **Storage:** 500GB SSD
- **Netzwerk:** 10GbE empfohlen

**Storage Node (optional):**
- **Hardware:** Mac Studio oder Mac Mini
- **RAM:** 32GB
- **Storage:** 2TB+ SSD
- **Netzwerk:** 10GbE empfohlen

### 2.2 Netzwerk-Infrastruktur

**VLAN-Konfiguration:**
- **VLAN 30 (Management):** 10.30.30.0/24
  - Ray Dashboard, SSH, Monitoring, Admin Interface
- **VLAN 10 (Worker/Cluster):** 10.10.10.0/24
  - Ray Worker Communication, Face Detection, Embedding Services
- **VLAN 20 (Storage):** 10.20.20.0/24
  - minIO, Object Storage, Data Transfer

**Port-Anforderungen:**

| Service | Port | Protokoll | VLAN | Beschreibung |
|---------|------|-----------|------|--------------|
| Ray Dashboard | 8265 | TCP | Management | Web-Interface für Ray Cluster |
| Ray GCS | 6380 | TCP | Management | Global Control Store |
| Ray Client | 10001 | TCP | Worker | Ray Worker Communication |
| Face Detection | 5001 | TCP | Worker | Face Detection Service |
| Embedding | 5002 | TCP | Worker | Embedding Service |
| LLM (exo) | 8000 | TCP | Management | LLM API Service |
| Admin Dashboard | 8080 | TCP | Management | Web-Admin-Interface |
| Prometheus | 9090 | TCP | Management | Metrics Collection |
| Grafana | 3000 | TCP | Management | Monitoring Dashboard |
| Metrics Collector | 9091 | TCP | Management | Custom Metrics Endpoint |
| minIO | 9000 | TCP | Storage | Object Storage API |
| minIO Console | 9001 | TCP | Storage | Object Storage Web UI |
| Neo4j | 7687 | TCP | Management | Graph Database (Bolt) |
| SSH | 22 | TCP | Management | Remote Access |

---

## 3. Software-Anforderungen

### 3.1 Betriebssystem
- **macOS:** 12.3+ (für MPS/MLX Support)
- **Architektur:** Apple Silicon (M1/M2/M3/M4) erforderlich

### 3.2 Python-Umgebung
- **Python:** 3.10+ (empfohlen: 3.12)
- **Virtual Environment:** mlx_env (wird automatisch erstellt)

### 3.3 Hauptabhängigkeiten
- MLX >= 0.29.0 (Apple Silicon ML Framework)
- Ray[default] >= 2.8.0 (Distributed Computing)
- Flask >= 2.3.0 (Web Services)
- minIO >= 7.0.0 (Object Storage)
- Neo4j >= 5.0.0 (Graph Database)
- Prometheus (Monitoring)
- Grafana (Visualization)

### 3.4 Zusätzliche Tools
- **Homebrew:** Für Package Management
- **Docker Desktop:** Optional, für Container-basiertes Deployment
- **Git:** Für Repository-Management

---

## 4. Netzwerk-Konfiguration

### 4.1 VLAN-Setup

**Management VLAN (30):**
```
Subnet: 10.30.30.0/24
Gateway: 10.30.30.1
DNS: 10.30.30.1, 8.8.8.8
Head Node IP: 10.30.30.10
```

**Worker VLAN (10):**
```
Subnet: 10.10.10.0/24
Gateway: 10.10.10.1
DNS: 10.10.10.1, 8.8.8.8
Worker Node 1 IP: 10.10.10.11
Worker Node 2 IP: 10.10.10.12
```

**Storage VLAN (20):**
```
Subnet: 10.20.20.0/24
Gateway: 10.20.20.1
DNS: 10.20.20.1, 8.8.8.8
Storage Node IP: 10.20.20.100
```

### 4.2 Firewall-Regeln

**Management VLAN:**
- Eingehend: 8265 (Ray Dashboard), 22 (SSH), 8080 (Admin)
- Ausgehend: Alle erlaubt

**Worker VLAN:**
- Eingehend: 10001 (Ray Worker), 5001 (Face Detection), 5002 (Embedding)
- Ausgehend: 10.30.30.0/24 (Management), 10.20.20.0/24 (Storage)

**Storage VLAN:**
- Eingehend: 9000 (minIO), 9001 (minIO Console)
- Ausgehend: 10.10.10.0/24 (Worker), 10.30.30.0/24 (Management)

### 4.3 Netzwerk-Performance
- **Bandbreite:** 10GbE empfohlen für Datenübertragung
- **Latenz:** < 1ms zwischen Nodes empfohlen
- **Jumbo Frames:** Optional, für bessere Performance

---

## 5. Sicherheit

### 5.1 Zugriffskontrolle
- **SSH:** Nur über Management VLAN (10.30.30.0/24)
- **Admin Dashboard:** Lokales Netzwerk oder VPN
- **Ray Dashboard:** Lokales Netzwerk
- **Grafana:** Lokales Netzwerk, Standard-Login ändern

### 5.2 Authentifizierung
- **Standard-Credentials ändern:**
  - Grafana: admin / admin (beim ersten Login ändern)
  - Neo4j: Standard-Passwort ändern
  - minIO: Access Keys ändern

### 5.3 Datenübertragung
- **Intern:** Unverschlüsselt (lokales Netzwerk)
- **Extern:** HTTPS/TLS empfohlen für Remote-Zugriff

---

## 6. Storage-Anforderungen

### 6.1 Lokaler Storage
- **Model Files:** ~50-100GB (GPT-OSS-120B)
- **Image Storage:** Abhängig von Workload
- **Logs:** ~10-50GB (rotierend)
- **Database:** ~5-20GB (Neo4j)

### 6.2 Object Storage (minIO)
- **Bucket:** incoming, processed, face-crops
- **Retention:** Konfigurierbar
- **Backup:** Externe Backup-Strategie empfohlen

---

## 7. Monitoring und Logging

### 7.1 Monitoring-Services
- **Prometheus:** Metriken-Sammlung (Port 9090)
- **Grafana:** Visualisierung (Port 3000)
- **Metrics Collector:** Custom Metrics (Port 9091)

### 7.2 Überwachte Metriken
- System: CPU, Memory, Disk Usage
- Ray Cluster: Nodes, CPUs, GPUs, Memory
- Services: Status, Response Times
- Network: Bandwidth, Latency

### 7.3 Logging
- **Service Logs:** `services/*.log`
- **Ray Logs:** `/tmp/ray/session_*/logs/`
- **Grafana Logs:** `monitoring/grafana/logs/`
- **Prometheus Logs:** Systemd/Launchd

---

## 8. Backup und Disaster Recovery

### 8.1 Backup-Strategie
- **Konfiguration:** Git Repository (automatisch)
- **Datenbank:** Neo4j Dumps (täglich)
- **Object Storage:** minIO Replication oder externe Backup
- **Model Files:** Externe Backup empfohlen

### 8.2 Recovery
- **Konfiguration:** Git Clone + Setup Scripts
- **Datenbank:** Neo4j Restore
- **Services:** Automatischer Neustart via Scripts

---

## 9. Deployment-Optionen

### 9.1 Native Installation
- Direkte Installation auf macOS
- Beste Performance für MLX
- Manuelle Konfiguration pro Node

### 9.2 Docker Deployment
- Container-basiertes Setup
- Einfache Node-Erstellung
- Portabel zwischen Macs

**Docker-Anforderungen:**
- Docker Desktop für Mac
- 16GB+ RAM für Container
- Netzwerk-Zugriff zwischen Nodes

---

## 10. Wartung und Updates

### 10.1 Regelmäßige Wartung
- **Log Rotation:** Automatisch konfiguriert
- **Disk Space Monitoring:** Via Grafana
- **Service Health Checks:** Automatisch
- **Security Updates:** Regelmäßig

### 10.2 Update-Prozess
1. Git Pull für Code-Updates
2. Dependencies aktualisieren: `pip install -e .`
3. Services neu starten: `./services/start_services.sh`
4. Ray Cluster neu starten: `./ray_cluster/start_ray_cluster.sh`

---

## 11. Support und Dokumentation

### 11.1 Dokumentation
- **README.md:** Hauptdokumentation
- **INSTALLATION.md:** Installationsanleitung
- **MONITORING.md:** Monitoring-Setup
- **VLAN_SETUP.md:** Netzwerk-Konfiguration
- **RAY_CLUSTER_SETUP.md:** Ray Cluster Setup

### 11.2 Repository
- **GitHub:** https://github.com/USERNAME/MacStudioCluster
- **Branch:** main
- **Submodules:** exo (LLM Framework)

---

## 12. Kontakt und Support

### 12.1 Technischer Ansprechpartner
- **Projekt:** Mac Studio Cluster - Face Tagging System
- **Repository:** Siehe GitHub Link
- **Dokumentation:** Siehe Projekt-README

### 12.2 Notfall-Kontakt
- Bei kritischen Problemen: Siehe Projekt-Dokumentation
- Logs prüfen: `services/*.log`, `monitoring/grafana/logs/`

---

## 13. Anhänge

### 13.1 Netzwerk-Diagramm
```
┌─────────────────────────────────────────────────────────┐
│                   Mac Studio Cluster                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Management   │  │ Worker 1     │  │ Worker 2     │  │
│  │ Node         │  │              │  │              │  │
│  │              │  │              │  │              │  │
│  │ Ray Head     │  │ Ray Worker   │  │ Ray Worker   │  │
│  │ LLM Service  │  │ Face Detect  │  │ Face Detect  │  │
│  │ Admin        │  │ Embedding    │  │ Embedding    │  │
│  │ Monitoring   │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                  │          │
│         └──────────────────┴──────────────────┘          │
│                    Ray Cluster Network                    │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 13.2 Port-Übersicht (Kompakt)

**Management Node:**
- 8000, 8080, 8265, 6380, 9090, 3000, 9091

**Worker Node:**
- 5001, 5002, 10001

**Storage Node:**
- 9000, 9001

---

## 14. Genehmigungen und Compliance

### 14.1 Erforderliche Genehmigungen
- Netzwerk-Zugriff für VLAN-Konfiguration
- Firewall-Regeln für oben genannte Ports
- Externer Zugriff (falls Remote-Monitoring gewünscht)

### 14.2 Compliance
- **Daten:** Gesichter und Bilder werden lokal verarbeitet
- **Speicherung:** Konfigurierbar (lokales Netzwerk)
- **Logging:** Keine persönlichen Daten in Logs

---

**Ende des Dokuments**

*Diese Konfiguration dient als Vorlage für das IT-Management-Team. Bitte passen Sie die IP-Adressen, VLANs und andere spezifische Konfigurationen an Ihre Umgebung an.*
