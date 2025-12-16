# Monitoring Setup für Mac Studio Cluster

Grafana und Prometheus Monitoring für den Mac Studio Cluster.

## Installation

```bash
./monitoring/install_monitoring.sh
```

Dies installiert:
- Grafana (über Homebrew)
- Prometheus (über Homebrew)
- Erstellt notwendige Konfigurationsdateien

## Services starten

### 1. Prometheus starten
```bash
./monitoring/start_prometheus.sh
```
- Web-Interface: http://localhost:9090

### 2. Metrics Collector starten
```bash
./monitoring/start_metrics_collector.sh
```
- Metrics Endpoint: http://localhost:9091/metrics
- Sammelt Metriken von:
  - System (CPU, Memory, Disk)
  - Ray Cluster
  - Services (Face Detection, Embedding, LLM, Admin)

### 3. Grafana starten
```bash
./monitoring/start_grafana.sh
```
- Dashboard: http://localhost:3000
- Standard-Login: `admin` / `admin`

## Alle Services stoppen

```bash
./monitoring/stop_monitoring.sh
```

## Dashboard

### Automatischer Import

Nach dem Start von Grafana sollte das Dashboard automatisch geladen werden. Falls nicht:

### Manueller Import

1. Öffne http://localhost:3000
2. Login mit `admin` / `admin`
3. Gehe zu: **Dashboards** → **Import** (oder + → Import)
4. Klicke auf **Upload JSON file**
5. Wähle die Datei: `monitoring/grafana/dashboards/cluster-dashboard.json`
6. Klicke auf **Load** und dann **Import**

### Über API importieren

```bash
# Erstelle API Key in Grafana (Configuration → API Keys)
# Dann:
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @monitoring/grafana/dashboards/cluster-dashboard.json
```

### Dashboard-Script

```bash
./monitoring/import_dashboard.sh
```

Dies zeigt dir die Import-Optionen an.

## Metriken

### System Metriken
- `system_cpu_percent` - CPU Auslastung in Prozent
- `system_memory_percent` - Memory Auslastung in Prozent
- `system_memory_used_bytes` - Verwendeter Speicher in Bytes
- `system_disk_percent` - Disk Auslastung in Prozent

### Ray Cluster Metriken
- `ray_nodes_count` - Anzahl der Ray Nodes
- `ray_cpus_available` - Verfügbare CPUs im Cluster
- `ray_gpus_available` - Verfügbare GPUs im Cluster

### Service Metriken
- `face_detection_status` - Status (1=online, 0=offline)
- `embedding_status` - Status
- `llm_status` - Status
- `admin_status` - Status
- `*_response_time` - Antwortzeit der Services

## Konfiguration

### Prometheus Config
`monitoring/prometheus/prometheus.yml`

### Grafana Datasource
`monitoring/grafana/provisioning/datasources/prometheus.yml`

### Grafana Dashboards
`monitoring/grafana/dashboards/`

## Troubleshooting

### Port bereits belegt
```bash
# Prüfe Ports
lsof -i :9090  # Prometheus
lsof -i :3000  # Grafana
lsof -i :9091  # Metrics Collector

# Beende Prozesse
kill $(lsof -ti :9090)
```

### Grafana Login-Problem
- Standard-Login: `admin` / `admin`
- Nach erstem Login wird Passwort-Änderung verlangt

### Metriken werden nicht angezeigt
1. Prüfe ob Metrics Collector läuft: `curl http://localhost:9091/metrics`
2. Prüfe Prometheus Targets: http://localhost:9090/targets
3. Prüfe Grafana Datasource: http://localhost:3000/connections/datasources

## Integration mit Admin-Seite

Die Admin-Seite kann über die API auf Monitoring-Status zugreifen:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Metrics: http://localhost:9091/metrics

