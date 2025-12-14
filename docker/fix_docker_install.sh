#!/bin/bash
# Script zum Beheben von Docker-Installationsproblemen

set -e

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info "=== Docker Installations-Fix ==="

# Prüfe ob alte Docker-Installation existiert
if [ -L "/usr/local/bin/hub-tool" ]; then
    log_warn "Alte Docker-Installation gefunden"
    log_info "Entferne alte Symlinks..."
    
    # Entferne alte Symlinks (benötigt sudo)
    sudo rm -f /usr/local/bin/hub-tool 2>/dev/null || log_warn "Konnte hub-tool nicht entfernen"
    sudo rm -rf /usr/local/cli-plugins 2>/dev/null || log_warn "Konnte cli-plugins nicht entfernen"
    
    log_info "Alte Symlinks entfernt"
fi

# Prüfe ob Docker.app existiert
if [ -d "/Applications/Docker.app" ]; then
    log_warn "Docker.app existiert bereits"
    log_info "Entferne alte Installation..."
    sudo rm -rf /Applications/Docker.app || log_warn "Konnte Docker.app nicht entfernen"
fi

# Installiere Docker über Homebrew
log_info "Installiere Docker Desktop..."
brew install --cask docker

log_info ""
log_info "=== Installation abgeschlossen ==="
log_info ""
log_info "Nächste Schritte:"
log_info "1. Starte Docker Desktop: open -a Docker"
log_info "2. Warte bis Docker vollständig gestartet ist"
log_info "3. Prüfe Installation: docker --version"
log_info ""
log_info "Falls Probleme auftreten, siehe: docker/INSTALL_DOCKER.md"
