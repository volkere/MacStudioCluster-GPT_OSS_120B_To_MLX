# VLAN-Konfiguration für Mac Studio Cluster

Anleitung zur Einrichtung von 3 VLANs für Management, Worker und Storage Nodes.

## Übersicht

Das Cluster nutzt 3 separate VLANs:

1. **VLAN 30 - Management** (10.30.30.0/24)
   - Head Node (Ray Dashboard, Monitoring)
   - SSH-Zugriff
   - Management-Services

2. **VLAN 10 - Worker/Cluster** (10.10.10.0/24)
   - Worker Nodes (Ray Workers)
   - Face Detection Service
   - Embedding Service
   - Compute-Workloads

3. **VLAN 20 - Storage** (10.20.20.0/24)
   - Storage Node (minIO, NAS)
   - Daten-Speicherung
   - Backup-Services

## Voraussetzungen

- **macOS** (für networksetup)
- **Root-Rechte** (sudo)
- **Managed Switch** mit VLAN-Support
- **Mehrere Netzwerk-Interfaces** (oder VLAN-tagging)

## Schnellstart

### 1. Head Node einrichten

```bash
cd network
sudo ./setup_vlan.sh head 10.30.30.10
```

### 2. Worker Node einrichten

```bash
sudo ./setup_vlan.sh worker 10.30.30.11 10.10.10.11
```

### 3. Storage Node einrichten

```bash
sudo ./setup_vlan.sh storage 10.30.30.100 10.20.20.100
```

### 4. VLAN-Status prüfen

```bash
# Teste Konnektivität
./test_vlan.sh

# Zeige VLAN-Status
networksetup -listVLANs
```

## Detaillierte Anleitung

### Head Node Setup

Der Head Node benötigt nur das Management VLAN:

```bash
sudo ./setup_vlan.sh head 10.30.30.10
```

**Konfiguration:**
- Management VLAN: 10.30.30.10/24
- Ray Dashboard: Port 8265
- SSH: Port 22

### Worker Node Setup

Worker Nodes benötigen Worker + Management VLAN:

```bash
sudo ./setup_vlan.sh worker 10.30.30.11 10.10.10.11
```

**Konfiguration:**
- Management VLAN: 10.30.30.11/24 (für SSH/Monitoring)
- Worker VLAN: 10.10.10.11/24 (für Compute)
- Ray Worker: Port 10001
- Face Detection: Port 5001
- Embedding: Port 5002

### Storage Node Setup

Storage Nodes benötigen Storage + Management VLAN:

```bash
sudo ./setup_vlan.sh storage 10.30.30.100 10.20.20.100
```

**Konfiguration:**
- Management VLAN: 10.30.30.100/24 (für SSH/Monitoring)
- Storage VLAN: 10.20.20.100/24 (für Storage)
- minIO: Port 9000
- minIO Console: Port 9001

## VLAN-Verwaltung

### VLAN-Status anzeigen

```bash
networksetup -listVLANs
```

### VLAN entfernen

```bash
sudo ./remove_vlan.sh
```

### Manuelle VLAN-Konfiguration

```bash
# VLAN erstellen
networksetup -createVLAN "Management-VLAN30" en0 30

# IP-Adresse setzen
networksetup -setmanual "Management-VLAN30" 10.30.30.10 255.255.255.0

# VLAN entfernen
networksetup -deleteVLAN "Management-VLAN30"
```

## Netzwerk-Testing

### Connectivity Test

```bash
./test_vlan.sh
```

Testet:
- Ping zu allen Nodes
- Port-Verfügbarkeit
- VLAN-Konfiguration

### Manuelle Tests

```bash
# Ping zu Head Node
ping 10.30.30.10

# Port-Test (Ray Dashboard)
nc -zv 10.30.30.10 8265

# Port-Test (Ray Worker)
nc -zv 10.10.10.11 10001

# Port-Test (minIO)
nc -zv 10.20.20.100 9000
```

## Konfiguration

### VLAN-Konfiguration anpassen

Editiere `vlan_config.yaml`:

```yaml
vlans:
  management:
    id: 30
    subnet: "10.30.30.0/24"
    nodes:
      - name: "head-node"
        ip: "10.30.30.10"
```

### Interface-Anpassung

Standard-Interfaces:
- `en0`: WiFi (für Management)
- `en1`: Ethernet (für Worker)
- `en2`: Zweite Ethernet (für Storage)

Anpassen in `setup_vlan.sh` oder via Parameter.

## Firewall-Konfiguration

### macOS Firewall

```bash
# System Preferences → Security & Privacy → Firewall
# Oder via Terminal:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/ray
```

### Port-Freigabe

**Management VLAN:**
- 8265 (Ray Dashboard)
- 22 (SSH)

**Worker VLAN:**
- 10001 (Ray Worker)
- 5001 (Face Detection)
- 5002 (Embedding)

**Storage VLAN:**
- 9000 (minIO)
- 9001 (minIO Console)

## Troubleshooting

### VLAN wird nicht erstellt

```bash
# Prüfe verfügbare Interfaces
networksetup -listallnetworkservices

# Prüfe Root-Rechte
sudo -v

# Prüfe Switch-Konfiguration (VLAN-tagging aktiviert?)
```

### Keine Verbindung zwischen VLANs

1. **Switch-Konfiguration prüfen:**
   - VLAN-tagging aktiviert?
   - Trunk-Ports konfiguriert?

2. **Routing prüfen:**
   ```bash
   route -n get 10.10.10.0/24
   ```

3. **Firewall prüfen:**
   ```bash
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps
   ```

### IP-Adresse wird nicht gesetzt

```bash
# Prüfe Interface-Status
ifconfig

# Manuell setzen
sudo ifconfig Management-VLAN30 10.30.30.10 netmask 255.255.255.0
```

## Netzwerk-Architektur

```
┌─────────────────────────────────────────────────────────┐
│              Managed 10/25GbE Switch                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  VLAN 30 (Management)                                   │
│  ├─→ Head Node: 10.30.30.10                            │
│  └─→ Worker Nodes: 10.30.30.11, 10.30.30.12           │
│                                                          │
│  VLAN 10 (Worker/Cluster)                               │
│  ├─→ Worker Node 1: 10.10.10.11                         │
│  └─→ Worker Node 2: 10.10.10.12                         │
│                                                          │
│  VLAN 20 (Storage)                                      │
│  └─→ Storage Node: 10.20.20.100                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Weitere Informationen

- [Haupt-README](../README.md)
- [Installation Guide](../INSTALLATION.md)
- [Ray Cluster Setup](../RAY_CLUSTER_SETUP.md)
