# VLAN Setup Guide - Mac Studio Cluster

Vollständige Anleitung zur Einrichtung von 3 VLANs für Management, Worker und Storage Nodes.

## 📋 Übersicht

Das Cluster nutzt 3 separate VLANs für optimale Netzwerk-Isolierung und Performance:

- **VLAN 30 - Management** (10.30.30.0/24)
- **VLAN 10 - Worker/Cluster** (10.10.10.0/24)
- **VLAN 20 - Storage** (10.20.20.0/24)

## 🚀 Schnellstart

### 1. Head Node (Management VLAN)

```bash
cd network
sudo ./setup_vlan.sh head 10.30.30.10
```

### 2. Worker Node (Worker + Management VLAN)

```bash
sudo ./setup_vlan.sh worker 10.30.30.11 10.10.10.11
```

### 3. Storage Node (Storage + Management VLAN)

```bash
sudo ./setup_vlan.sh storage 10.30.30.100 10.20.20.100
```

### 4. Testen

```bash
./test_vlan.sh
```

## 📐 Netzwerk-Architektur

```
┌─────────────────────────────────────────────────────────────┐
│         Managed 10/25GbE Switch (VLAN-tagging)              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  VLAN 30 (Management) - 10.30.30.0/24                      │
│  ├─→ Head Node: 10.30.30.10                                │
│  │   ├─ Ray Dashboard (8265)                               │
│  │   ├─ SSH (22)                                           │
│  │   └─ Monitoring (9090)                                  │
│  ├─→ Worker Node 1: 10.30.30.11 (SSH/Monitoring)          │
│  └─→ Storage Node: 10.30.30.100 (SSH/Monitoring)           │
│                                                              │
│  VLAN 10 (Worker/Cluster) - 10.10.10.0/24                 │
│  ├─→ Worker Node 1: 10.10.10.11                            │
│  │   ├─ Ray Worker (10001)                                │
│  │   ├─ Face Detection (5001)                             │
│  │   └─ Embedding (5002)                                   │
│  └─→ Worker Node 2: 10.10.10.12                            │
│      ├─ Ray Worker (10001)                                │
│      ├─ Face Detection (5001)                             │
│      └─ Embedding (5002)                                   │
│                                                              │
│  VLAN 20 (Storage) - 10.20.20.0/24                        │
│  └─→ Storage Node: 10.20.20.100                            │
│      ├─ minIO (9000)                                      │
│      └─ minIO Console (9001)                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Detaillierte Einrichtung

### Voraussetzungen

1. **Managed Switch** mit VLAN-Support
2. **VLAN-tagging** auf Switch aktiviert
3. **Root-Rechte** auf allen Macs
4. **Netzwerk-Interfaces** identifiziert

### Schritt 1: Switch-Konfiguration

Auf dem Managed Switch:

1. **VLANs erstellen:**
   - VLAN 10: Worker/Cluster
   - VLAN 20: Storage
   - VLAN 30: Management

2. **Trunk-Ports konfigurieren:**
   - Ports zu Macs als Trunk-Ports
   - Alle VLANs erlauben (10, 20, 30)

3. **Access-Ports (optional):**
   - NAS auf VLAN 20
   - Router auf VLAN 30

### Schritt 2: Head Node Setup

```bash
# 1. VLAN einrichten
cd /path/to/MacStudioCluster/network
sudo ./setup_vlan.sh head 10.30.30.10

# 2. Verifikation
ifconfig | grep "10.30.30.10"
networksetup -listVLANs

# 3. Services starten (auf Management VLAN)
cd ..
./ray_cluster/start_ray_cluster.sh head
./services/start_services.sh
```

**Konfiguration:**
- Management VLAN: 10.30.30.10/24
- Ray Dashboard: http://10.30.30.10:8265
- SSH: 10.30.30.10:22

### Schritt 3: Worker Node Setup

```bash
# 1. VLANs einrichten (Worker + Management)
sudo ./setup_vlan.sh worker 10.30.30.11 10.10.10.11

# 2. Verifikation
ifconfig | grep -E "10.30.30.11|10.10.10.11"

# 3. Ray Worker starten (auf Worker VLAN)
cd ..
./ray_cluster/start_ray_cluster.sh worker 10.30.30.10:10001

# 4. Services starten (auf Worker VLAN)
./services/start_services.sh
```

**Konfiguration:**
- Management VLAN: 10.30.30.11/24 (SSH/Monitoring)
- Worker VLAN: 10.10.10.11/24 (Compute)
- Ray Worker: 10.10.10.11:10001
- Face Detection: 10.10.10.11:5001
- Embedding: 10.10.10.11:5002

### Schritt 4: Storage Node Setup

```bash
# 1. VLANs einrichten (Storage + Management)
sudo ./setup_vlan.sh storage 10.30.30.100 10.20.20.100

# 2. Verifikation
ifconfig | grep -E "10.30.30.100|10.20.20.100"

# 3. minIO starten (auf Storage VLAN)
# minIO sollte auf 10.20.20.100:9000 laufen
```

**Konfiguration:**
- Management VLAN: 10.30.30.100/24 (SSH/Monitoring)
- Storage VLAN: 10.20.20.100/24 (Storage)
- minIO: 10.20.20.100:9000
- minIO Console: 10.20.20.100:9001

## 🧪 Testing

### Connectivity Test

```bash
cd network
./test_vlan.sh
```

### Manuelle Tests

```bash
# Management VLAN
ping 10.30.30.10
nc -zv 10.30.30.10 8265  # Ray Dashboard

# Worker VLAN
ping 10.10.10.11
nc -zv 10.10.10.11 10001  # Ray Worker
nc -zv 10.10.10.11 5001   # Face Detection

# Storage VLAN
ping 10.20.20.100
nc -zv 10.20.20.100 9000  # minIO
```

### Ray Cluster Test

```bash
# Auf Head Node
ray status

# Von Worker Node
ray status  # Sollte Head Node sehen
```

## ⚙️ Konfiguration anpassen

### IP-Adressen ändern

Editiere `network/vlan_config.yaml`:

```yaml
vlans:
  management:
    nodes:
      - name: "head-node"
        ip: "10.30.30.10"  # Ändern
```

### Interface-Anpassung

Standard-Interfaces:
- `en0`: WiFi (Management)
- `en1`: Ethernet (Worker)
- `en2`: Zweite Ethernet (Storage)

Anpassen in `setup_vlan.sh` oder manuell:

```bash
networksetup -createVLAN "Worker-VLAN10" en1 10
```

## 🔒 Firewall-Konfiguration

### macOS Firewall

```bash
# System Preferences → Security & Privacy → Firewall
# Oder:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/ray
```

### Port-Freigabe pro VLAN

**Management VLAN (10.30.30.0/24):**
- 8265: Ray Dashboard
- 22: SSH
- 9090: Monitoring

**Worker VLAN (10.10.10.0/24):**
- 10001: Ray Worker
- 5001: Face Detection
- 5002: Embedding

**Storage VLAN (10.20.20.0/24):**
- 9000: minIO
- 9001: minIO Console

## 🐛 Troubleshooting

### VLAN wird nicht erstellt

```bash
# Prüfe verfügbare Interfaces
networksetup -listallnetworkservices

# Prüfe Root-Rechte
sudo -v

# Prüfe Switch-Konfiguration
# - VLAN-tagging aktiviert?
# - Trunk-Ports konfiguriert?
```

### Keine Verbindung zwischen VLANs

1. **Switch-Konfiguration:**
   - Trunk-Ports richtig konfiguriert?
   - VLANs auf Switch erstellt?

2. **Routing:**
   ```bash
   route -n get 10.10.10.0/24
   ```

3. **Firewall:**
   ```bash
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps
   ```

### Services nicht erreichbar

1. **Prüfe Service-IPs:**
   ```bash
   # Services sollten auf richtigen VLAN-IPs laufen
   netstat -an | grep LISTEN
   ```

2. **Prüfe Konfiguration:**
   ```bash
   # pipeline/config.yaml
   # ray_cluster/config.yaml
   ```

3. **Teste Connectivity:**
   ```bash
   ./test_vlan.sh
   ```

## 📚 Weitere Informationen

- [Network README](network/README.md) - Detaillierte Netzwerk-Dokumentation
- [Installation Guide](INSTALLATION.md) - Vollständige Installation
- [Ray Cluster Setup](RAY_CLUSTER_SETUP.md) - Ray Cluster Konfiguration
- [Haupt-README](README.md) - Projekt-Übersicht

## 🔗 Nützliche Befehle

```bash
# VLAN-Status
networksetup -listVLANs

# IP-Adressen
ifconfig | grep "inet "

# Routing-Tabelle
netstat -rn

# Port-Status
netstat -an | grep LISTEN

# VLAN entfernen
sudo ./remove_vlan.sh
```
