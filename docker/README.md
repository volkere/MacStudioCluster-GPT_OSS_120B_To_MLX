# Docker Setup für Mac Studio Cluster

Einfaches Multi-Node Setup mit Docker. Starte einen neuen Node auf einem anderen Mac mit einem einzigen Befehl.

## Voraussetzungen

- **Docker Desktop** für Mac installiert
- **Apple Silicon** (M1/M2/M3/M4) empfohlen
- **Netzwerk:** Alle Macs im gleichen Netzwerk

## Schnellstart

### 1. Management Node (Head) starten

Auf dem ersten Mac:

```bash
cd docker
./start-node.sh management
```

Dies startet:
- Ray Head Node
- LLM Service (exo)
- Admin Server
- Monitoring (Grafana, Prometheus)

### 2. Worker Node starten

Auf einem anderen Mac:

```bash
# Klone Repository
git clone <repository-url>
cd MacStudioCluster/docker

# Starte Worker Node
./start-node.sh worker <head-ip>:6380
```

Beispiel:
```bash
./start-node.sh worker 192.168.1.100:6380
```

## Docker Compose

### Alle Services starten

```bash
cd docker
docker-compose up -d
```

### Einzelne Services

```bash
# Nur Management Node
docker-compose up -d management

# Nur Worker Node
docker-compose up -d worker1

# Mit mehreren Worker Nodes
docker-compose --profile multi-worker up -d
```

### Services stoppen

```bash
docker-compose down
```

## Konfiguration

### Environment Variables

Erstelle `.env` Datei:

```env
NODE_TYPE=worker
RAY_HEAD_ADDRESS=192.168.1.100:6380
RAY_CPUS=16
RAY_GPUS=1
ENABLE_MONITORING=false
```

### Ports

**Management Node:**
- 8000: LLM Service
- 8080: Admin Server
- 8265: Ray Dashboard
- 6380: Ray GCS
- 9090: Prometheus
- 3000: Grafana
- 9091: Metrics Collector

**Worker Node:**
- 5001: Face Detection
- 5002: Embedding
- 10001: Ray Worker

## Zugriff

Nach dem Start:

- **Admin Dashboard:** http://localhost:8080
- **Ray Dashboard:** http://localhost:8265
- **Grafana:** http://localhost:3000 (nur Management)
- **Prometheus:** http://localhost:9090 (nur Management)

## Troubleshooting

### Container startet nicht

```bash
# Prüfe Logs
docker-compose logs

# Prüfe Container-Status
docker-compose ps
```

### Port bereits belegt

Ändere Ports in `docker-compose.yml`:

```yaml
ports:
  - "8081:8080"  # Anderer Port
```

### Worker kann Head nicht erreichen

1. Prüfe Firewall-Einstellungen
2. Prüfe Netzwerk-Konnektivität:
   ```bash
   ping <head-ip>
   nc -zv <head-ip> 6380
   ```
3. Prüfe ob Head Node läuft:
   ```bash
   curl http://<head-ip>:8265
   ```

### MLX funktioniert nicht

MLX benötigt Apple Silicon und Metal. Im Container läuft MLX möglicherweise nicht optimal. Für Produktion:

1. Nutze native Installation auf dem Host
2. Oder verwende Docker nur für Services ohne MLX

## Erweiterte Konfiguration

### Mehrere Worker Nodes

```bash
# Starte mehrere Worker
docker-compose --profile multi-worker up -d worker1 worker2
```

### Custom Build

```bash
# Baue Image neu
docker-compose build

# Baue spezifischen Service
docker-compose build worker1
```

### Volumes

Daten werden in Docker Volumes gespeichert:
- `management-data`
- `worker1-data`
- `worker2-data`

Volumes anzeigen:
```bash
docker volume ls | grep mac-studio
```

## Unterschiede zu nativer Installation

- **MLX:** Läuft möglicherweise nicht optimal im Container
- **Performance:** Native Installation ist schneller
- **Netzwerk:** Docker Network statt VLANs
- **Einfachheit:** Ein Befehl zum Starten

## Migration von nativer Installation

1. Exportiere Konfiguration:
   ```bash
   cp pipeline/config.yaml docker/config/
   ```

2. Starte Container:
   ```bash
   ./start-node.sh worker <head-ip>:6380
   ```

3. Prüfe Verbindung:
   ```bash
   docker-compose exec worker1 ray status
   ```

## Weitere Ressourcen

- [Docker Dokumentation](https://docs.docker.com/)
- [Docker Compose Dokumentation](https://docs.docker.com/compose/)
- [Haupt-README](../README.md)
