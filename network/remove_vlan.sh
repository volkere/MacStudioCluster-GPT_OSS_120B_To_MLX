#!/bin/bash
# VLAN Entfernen Script für macOS

set -e

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funktionen
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Prüfe Root-Rechte
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Dieses Script benötigt Root-Rechte (sudo)"
        exit 1
    fi
}

# Entferne VLAN-Interface
remove_vlan() {
    local vlan_name=$1
    
    log_info "Entferne VLAN-Interface: $vlan_name"
    
    if ! networksetup -listVLANs | grep -q "$vlan_name"; then
        log_warn "VLAN-Interface '$vlan_name' existiert nicht"
        return 0
    fi
    
    networksetup -deleteVLAN "$vlan_name" || {
        log_error "Fehler beim Entfernen von VLAN-Interface"
        return 1
    }
    
    log_info "VLAN-Interface '$vlan_name' erfolgreich entfernt"
}

# Hauptfunktion
main() {
    log_info "=== VLAN Entfernen ==="
    
    check_root
    
    # Entferne alle Cluster-VLANs
    remove_vlan "Management-VLAN30"
    remove_vlan "Worker-VLAN10"
    remove_vlan "Storage-VLAN20"
    
    log_info ""
    log_info "=== Alle VLANs entfernt ==="
}

main "$@"


