#!/bin/bash
# VLAN Setup Script für macOS
# Konfiguriert 3 VLANs: Management, Worker, Storage

set -e

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/vlan_config.yaml"

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

# Prüfe ob networksetup verfügbar ist
check_networksetup() {
    if ! command -v networksetup &> /dev/null; then
        log_error "networksetup nicht gefunden (nur auf macOS verfügbar)"
        exit 1
    fi
}

# Liste verfügbare Netzwerk-Interfaces
list_interfaces() {
    log_info "Verfügbare Netzwerk-Interfaces:"
    networksetup -listallnetworkservices | tail -n +2
}

# Erstelle VLAN-Interface
create_vlan_interface() {
    local parent_interface=$1
    local vlan_id=$2
    local vlan_name=$3
    local ip_address=$4
    local netmask=$5
    
    log_info "Erstelle VLAN-Interface: $vlan_name (VLAN $vlan_id auf $parent_interface)"
    
    # Prüfe ob VLAN bereits existiert
    if networksetup -listVLANs | grep -q "$vlan_name"; then
        log_warn "VLAN-Interface '$vlan_name' existiert bereits"
        return 0
    fi
    
    # Erstelle VLAN-Interface
    networksetup -createVLAN "$vlan_name" "$parent_interface" "$vlan_id" || {
        log_error "Fehler beim Erstellen von VLAN-Interface"
        return 1
    }
    
    # Konfiguriere IP-Adresse
    networksetup -setmanual "$vlan_name" "$ip_address" "$netmask" || {
        log_error "Fehler beim Setzen der IP-Adresse"
        return 1
    }
    
    log_info "VLAN-Interface '$vlan_name' erfolgreich erstellt"
    return 0
}

# Konfiguriere Management VLAN
setup_management_vlan() {
    local node_type=$1
    local node_ip=$2
    
    log_info "=== Setup Management VLAN (VLAN 30) ==="
    
    # Lese Konfiguration aus YAML (vereinfacht, für Produktion sollte yq verwendet werden)
    local parent_interface="en0"  # Standard: WiFi, kann angepasst werden
    local vlan_id=30
    local vlan_name="Management-VLAN30"
    local netmask="255.255.255.0"
    
    create_vlan_interface "$parent_interface" "$vlan_id" "$vlan_name" "$node_ip" "$netmask"
    
    log_info "Management VLAN konfiguriert: $node_ip/24"
}

# Konfiguriere Worker VLAN
setup_worker_vlan() {
    local node_type=$1
    local node_ip=$2
    
    log_info "=== Setup Worker VLAN (VLAN 10) ==="
    
    local parent_interface="en1"  # Standard: Ethernet, kann angepasst werden
    local vlan_id=10
    local vlan_name="Worker-VLAN10"
    local netmask="255.255.255.0"
    
    create_vlan_interface "$parent_interface" "$vlan_id" "$vlan_name" "$node_ip" "$netmask"
    
    log_info "Worker VLAN konfiguriert: $node_ip/24"
}

# Konfiguriere Storage VLAN
setup_storage_vlan() {
    local node_type=$1
    local node_ip=$2
    
    log_info "=== Setup Storage VLAN (VLAN 20) ==="
    
    local parent_interface="en2"  # Dritte NIC oder VLAN-Interface
    local vlan_id=20
    local vlan_name="Storage-VLAN20"
    local netmask="255.255.255.0"
    
    create_vlan_interface "$parent_interface" "$vlan_id" "$vlan_name" "$node_ip" "$netmask"
    
    log_info "Storage VLAN konfiguriert: $node_ip/24"
}

# Hauptfunktion
main() {
    local node_type=$1  # head, worker, storage
    local management_ip=$2
    local worker_ip=$3
    local storage_ip=$4
    
    log_info "=== VLAN Setup für Mac Studio Cluster ==="
    
    check_root
    check_networksetup
    
    log_info "Node-Typ: $node_type"
    
    # Liste verfügbare Interfaces
    list_interfaces
    
    # Setup basierend auf Node-Typ
    case "$node_type" in
        head)
            if [ -z "$management_ip" ]; then
                management_ip="10.30.30.10"
            fi
            setup_management_vlan "$node_type" "$management_ip"
            ;;
        worker)
            if [ -z "$worker_ip" ]; then
                worker_ip="10.10.10.11"
            fi
            if [ -z "$management_ip" ]; then
                management_ip="10.30.30.11"
            fi
            setup_worker_vlan "$node_type" "$worker_ip"
            setup_management_vlan "$node_type" "$management_ip"
            ;;
        storage)
            if [ -z "$storage_ip" ]; then
                storage_ip="10.20.20.100"
            fi
            if [ -z "$management_ip" ]; then
                management_ip="10.30.30.100"
            fi
            setup_storage_vlan "$node_type" "$storage_ip"
            setup_management_vlan "$node_type" "$management_ip"
            ;;
        all)
            # Alle VLANs auf einem Node (für Testing)
            setup_management_vlan "all" "${management_ip:-10.30.30.10}"
            setup_worker_vlan "all" "${worker_ip:-10.10.10.10}"
            setup_storage_vlan "all" "${storage_ip:-10.20.20.10}"
            ;;
        *)
            log_error "Unbekannter Node-Typ: $node_type"
            log_info "Verwendung: $0 {head|worker|storage|all} [management_ip] [worker_ip] [storage_ip]"
            exit 1
            ;;
    esac
    
    log_info ""
    log_info "=== VLAN Setup abgeschlossen ==="
    log_info "Prüfe Konfiguration mit: networksetup -listVLANs"
    log_info "Prüfe IP-Adressen mit: ifconfig"
}

# Hilfe anzeigen
show_help() {
    cat << EOF
VLAN Setup Script für Mac Studio Cluster

Verwendung:
  sudo $0 <node-type> [management_ip] [worker_ip] [storage_ip]

Node-Typen:
  head      - Head Node (nur Management VLAN)
  worker    - Worker Node (Worker + Management VLAN)
  storage   - Storage Node (Storage + Management VLAN)
  all       - Alle VLANs (für Testing)

Beispiele:
  # Head Node
  sudo $0 head 10.30.30.10
  
  # Worker Node
  sudo $0 worker 10.30.30.11 10.10.10.11
  
  # Storage Node
  sudo $0 storage 10.30.30.100 10.20.20.100
  
  # Alle VLANs (Testing)
  sudo $0 all 10.30.30.10 10.10.10.10 10.20.20.10

Hinweise:
  - Benötigt Root-Rechte (sudo)
  - Funktioniert nur auf macOS
  - Prüfe verfügbare Interfaces mit: networksetup -listallnetworkservices
EOF
}

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
    exit 0
fi

if [ $# -lt 1 ]; then
    show_help
    exit 1
fi

main "$@"


