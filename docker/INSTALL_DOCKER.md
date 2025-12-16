# Docker Installation auf macOS

## Option 1: Homebrew (Empfohlen)

```bash
brew install --cask docker
```

Nach der Installation:
1. Öffne Docker Desktop aus dem Applications Ordner
2. Oder starte es mit: `open -a Docker`
3. Warte bis Docker Desktop vollständig gestartet ist (Whale-Icon in der Menüleiste)

## Option 2: Manuelle Installation

1. Lade Docker Desktop herunter:
   - https://www.docker.com/products/docker-desktop/
   - Wähle "Download for Mac" (Apple Silicon)

2. Installiere Docker Desktop:
   - Öffne die heruntergeladene `.dmg` Datei
   - Ziehe Docker.app in den Applications Ordner
   - Öffne Docker Desktop aus Applications

3. Starte Docker Desktop:
   - Beim ersten Start musst du den Lizenzbedingungen zustimmen
   - Docker Desktop startet automatisch

## Verifikation

Nach der Installation prüfe:

```bash
docker --version
docker-compose --version
```

Sollte zeigen:
```
Docker version 24.x.x
Docker Compose version v2.x.x
```

## Docker Desktop starten

Falls Docker nicht läuft:

```bash
# Starte Docker Desktop
open -a Docker

# Oder über Spotlight: Cmd+Space → "Docker" → Enter
```

## Troubleshooting

### Docker läuft nicht

1. Prüfe ob Docker Desktop läuft:
   ```bash
   ps aux | grep -i docker
   ```

2. Starte Docker Desktop manuell:
   ```bash
   open -a Docker
   ```

3. Prüfe Docker Status:
   ```bash
   docker info
   ```

### Permission Denied

Falls du "permission denied" Fehler bekommst:

1. Stelle sicher, dass Docker Desktop läuft
2. Prüfe ob du in der `docker` Gruppe bist (normalerweise automatisch)
3. Starte Docker Desktop neu

### Apple Silicon (M1/M2/M3/M4)

Docker Desktop für Apple Silicon ist verfügbar und funktioniert nativ.
Die Installation erkennt automatisch deine Architektur.

## Nächste Schritte

Nach erfolgreicher Installation:

```bash
cd docker
./start-node.sh management
```

Oder für einen Worker Node:

```bash
./start-node.sh worker <head-ip>:6380
```


