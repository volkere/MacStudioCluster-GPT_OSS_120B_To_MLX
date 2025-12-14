# Monitoring Dokumentation - Mac Studio Cluster

Vollständige Dokumentation für das Grafana und Prometheus Monitoring Setup.

## Übersicht

Das Monitoring-System besteht aus drei Hauptkomponenten:

1. **Prometheus** - Metriken-Sammlung und -Speicherung
2. **Metrics Collector** - Python-Service der Metriken von System, Ray und Services sammelt
3. **Grafana** - Visualisierung und Dashboards

## Installation

### Automatische Installation

```bash
cd /Users/blaubaer/Documents/Aphrodite/MacStudioCluster
./monitoring/install_monitoring.sh
```

Dies installiert:
- Grafana (über Homebrew)
- Prometheus (über Homebrew)
- Erstellt alle notwendigen Konfigurationsdateien

### Manuelle Installation

Falls die automatische Installation fehlschlägt:

```bash
# Installiere Grafana
brew install grafana

# Installiere Prometheus
brew install prometheus
```

## Services starten

### Reihenfolge

Die Services sollten in dieser Reihenfolge gestartet werden:

1. **Prometheus** (Port 9090)
2. **Metrics Collector** (Port 9091)
3. **Grafana** (Port 3000)

### Start-Scripts

```bash
# 1. Prometheus
./monitoring/start_prometheus.sh

# 2. Metrics Collector
./monitoring/start_metrics_collector.sh

# 3. Grafana
./monitoring/start_grafana.sh
```

### Über Admin-Seite

1. Öffne http://localhost:8080
2. Gehe zum Tab "Monitoring"
3. Starte die Services in der richtigen Reihenfolge
4. Klicke auf "Öffnen" bei Grafana

## Zugriff

### Grafana Dashboard

- **URL:** http://localhost:3000
- **Standard-Login:** `admin` / `admin`
- **Hinweis:** Beim ersten Login wird eine Passwort-Änderung empfohlen

### Prometheus

- **URL:** http://localhost:9090
- **Targets:** http://localhost:9090/targets
- **Query:** http://localhost:9090/graph

### Metrics Collector

- **Health Check:** http://localhost:9091/health
- **Metrics Endpoint:** http://localhost:9091/metrics

## Verfügbare Metriken

### System Metriken

- `system_cpu_percent` - CPU Auslastung in Prozent
- `system_memory_percent` - Memory Auslastung in Prozent
- `system_memory_used_bytes` - Verwendeter Speicher in Bytes
- `system_disk_percent` - Disk Auslastung in Prozent

### Ray Cluster Metriken

- `ray_nodes_count` - Anzahl der Ray Nodes
- `ray_cpus_available` - Verfügbare CPUs im Cluster
- `ray_gpus_available` - Verfügbare GPUs im Cluster
- `ray_cpus_total` - Gesamte CPUs im Cluster
- `ray_gpus_total` - Gesamte GPUs im Cluster

### Service Metriken

- `face_detection_status` - Status (1=online, 0=offline)
- `embedding_status` - Status
- `llm_status` - Status
- `admin_status` - Status
- `*_response_time` - Antwortzeit der Services in Sekunden

## Dashboard

### Mac Studio Cluster Dashboard

Das Dashboard wird automatisch geladen und zeigt:

1. **CPU Usage** - Graph der CPU-Auslastung
2. **Memory Usage** - Graph der Memory-Auslastung
3. **Ray Cluster Nodes** - Anzahl der aktiven Nodes
4. **Ray CPUs/GPUs Available** - Verfügbare Ressourcen
5. **Service Status** - Tabelle mit Status aller Services
6. **Disk Usage** - Graph der Disk-Auslastung

### Dashboard anpassen

1. Öffne Grafana: http://localhost:3000
2. Gehe zu Dashboards → Mac Studio Cluster Dashboard
3. Klicke auf "Edit"
4. Passe Panels nach Bedarf an
5. Speichere das Dashboard

## Konfiguration

### Prometheus Config

Datei: `monitoring/prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'cluster-metrics'
    static_configs:
      - targets: ['localhost:9091']
```

### Grafana Datasource

Datei: `monitoring/grafana/provisioning/datasources/prometheus.yml`

Wird automatisch konfiguriert und verbindet Grafana mit Prometheus.

### Grafana Dashboards

Datei: `monitoring/grafana/dashboards/cluster-dashboard.json`

Das Dashboard wird automatisch geladen.

## Services stoppen

### Alle Services stoppen

```bash
./monitoring/stop_monitoring.sh
```

### Einzelne Services stoppen

```bash
# Über Admin-Seite
# Tab "Monitoring" → Service → "Stop"

# Oder manuell
pkill -f prometheus
pkill -f grafana-server
pkill -f metrics_collector
```

## Troubleshooting

### Port bereits belegt

```bash
# Prüfe Ports
lsof -i :9090  # Prometheus
lsof -i :3000  # Grafana
lsof -i :9091  # Metrics Collector

# Beende Prozesse
kill $(lsof -ti :9090)
kill $(lsof -ti :3000)
kill $(lsof -ti :9091)
```

### Grafana Login-Problem

- Standard-Login: `admin` / `admin`
- Falls Login fehlschlägt, prüfe ob Grafana läuft: `lsof -i :3000`
- Grafana Logs: `monitoring/grafana/logs/`

### Metriken werden nicht angezeigt

1. **Prüfe Metrics Collector:**
   ```bash
   curl http://localhost:9091/metrics
   ```

2. **Prüfe Prometheus Targets:**
   - Öffne http://localhost:9090/targets
   - Status sollte "UP" sein

3. **Prüfe Grafana Datasource:**
   - Öffne http://localhost:3000/connections/datasources
   - Prometheus sollte als Datasource konfiguriert sein

### Ray Metriken fehlen

- Stelle sicher, dass Ray Cluster läuft
- Prüfe ob Ray initialisiert ist: `ray status`
- Metrics Collector benötigt Zugriff auf Ray

### Service Metriken fehlen

- Prüfe ob Services laufen:
  ```bash
  lsof -i :5001  # Face Detection
  lsof -i :5002  # Embedding
  lsof -i :8000  # LLM
  lsof -i :8080  # Admin
  ```

## Erweiterte Konfiguration

### Metriken-Intervall ändern

In `monitoring/metrics_collector.py`:

```python
self.update_interval = 5.0  # Sekunden
```

### Prometheus Retention

In `monitoring/prometheus/prometheus.yml`:

```yaml
storage:
  tsdb:
    retention.time: 15d  # Daten 15 Tage behalten
```

### Grafana Alerting

Grafana unterstützt Alerting:
1. Öffne Dashboard → Panel → Edit
2. Gehe zu "Alert"
3. Konfiguriere Alert-Regeln

## Integration mit Admin-Seite

Die Admin-Seite bietet vollständige Integration:

- **Status-Anzeige:** Zeigt ob Services laufen
- **Start/Stop Buttons:** Direkte Steuerung
- **Links:** Direkte Links zu Grafana und Prometheus

Zugriff: http://localhost:8080 → Tab "Monitoring"

## Weitere Ressourcen

- [Grafana Dokumentation](https://grafana.com/docs/)
- [Prometheus Dokumentation](https://prometheus.io/docs/)
- [Monitoring README](monitoring/README.md)
