#!/bin/bash
# VLAN Test Script
# Testet Konnektivität zwischen VLANs

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

# Teste Ping
test_ping() {
    local target=$1
    local description=$2
    
    log_info "Teste Ping zu $description ($target)..."
    
    if ping -c 3 -W 2 "$target" > /dev/null 2>&1; then
        log_info "✓ $description erreichbar"
        return 0
    else
        log_error "✗ $description nicht erreichbar"
        return 1
    fi
}

# Teste Port
test_port() {
    local target=$1
    local port=$2
    local description=$3
    
    log_info "Teste Port $port auf $description ($target)..."
    
    if nc -zv -w 2 "$target" "$port" > /dev/null 2>&1; then
        log_info "✓ Port $port auf $description offen"
        return 0
    else
        log_warn "✗ Port $port auf $description nicht erreichbar"
        return 1
    fi
}

# Zeige Netzwerk-Interfaces
show_interfaces() {
    log_info "=== Netzwerk-Interfaces ==="
    ifconfig | grep -E "^[a-z]|inet " | grep -v "127.0.0.1"
}

# Zeige VLAN-Status
show_vlans() {
    log_info "=== VLAN-Status ==="
    if command -v networksetup &> /dev/null; then
        networksetup -listVLANs 2>/dev/null || log_warn "Keine VLANs konfiguriert"
    else
        log_warn "networksetup nicht verfügbar"
    fi
}

# Hauptfunktion
main() {
    log_info "=== VLAN Connectivity Test ==="
    
    # Zeige aktuelle Konfiguration
    show_interfaces
    echo ""
    show_vlans
    echo ""
    
    # Teste Management VLAN
    log_info "=== Management VLAN (10.30.30.0/24) ==="
    test_ping "10.30.30.1" "Management Gateway" || true
    test_ping "10.30.30.10" "Head Node" || true
    test_port "10.30.30.10" "8265" "Ray Dashboard" || true
    test_port "10.30.30.10" "22" "SSH" || true
    
    echo ""
    
    # Teste Worker VLAN
    log_info "=== Worker VLAN (10.10.10.0/24) ==="
    test_ping "10.10.10.1" "Worker Gateway" || true
    test_ping "10.10.10.11" "Worker Node 1" || true
    test_ping "10.10.10.12" "Worker Node 2" || true
    test_port "10.10.10.11" "10001" "Ray Worker" || true
    test_port "10.10.10.11" "5001" "Face Detection" || true
    test_port "10.10.10.11" "5002" "Embedding" || true
    
    echo ""
    
    # Teste Storage VLAN
    log_info "=== Storage VLAN (10.20.20.0/24) ==="
    test_ping "10.20.20.1" "Storage Gateway" || true
    test_ping "10.20.20.100" "Storage Node" || true
    test_port "10.20.20.100" "9000" "minIO" || true
    test_port "10.20.20.100" "9001" "minIO Console" || true
    
    echo ""
    log_info "=== Test abgeschlossen ==="
}

main "$@"
