# Mac Studio Cluster - Netzwerkarchitektur

---

## Übersicht

Präsentation der Netzwerkarchitektur für einen Mac Studio Cluster mit Storage und Management-Komponenten

---

## Netzwerk-Topologie

### Zentrale Komponenten

- **Internet / Management** als Ausgangspunkt
- **Router/VPN/DHCP** für Netzwerkverwaltung
- **Managed 10/25GbE Switch** als zentrale Verteilungsstelle

---

## VLAN-Struktur

Das Netzwerk ist in drei VLANs unterteilt:

1. **VLAN10** - Cluster
2. **VLAN20** - Storage
3. **VLAN30** - Management

---

## VLAN10 - Cluster

### Mac Studio M3 (Compute)
- **IP-Adresse:** 10.10.10.11
- **Funktion:** Compute Node
- **Optional:** Zweite NIC für Management VLAN
  - SSH/Updates über Management VLAN

---

## VLAN20 - Storage

### NAS (Network Attached Storage)
- **IP-Adresse:** 10.20.20.100
- **Anbindung:** 10GbE
- **Funktion:** Zentraler Speicher für den Cluster

---

## VLAN30 - Management

### Mac Studio M4 (Compute)
- **IP-Adresse:** 10.10.10.12
- **Funktion:** Compute Node
- **Zweck:** Management und andere Services

---

## Netzwerkarchitektur - Zusammenfassung

### Vorteile der VLAN-Trennung

- **Isolierung:** Separate Netzwerke für verschiedene Funktionen
- **Sicherheit:** Management-Traffic getrennt vom Cluster-Traffic
- **Performance:** Dedizierte Storage-Verbindung über 10GbE
- **Skalierbarkeit:** Einfache Erweiterung um weitere Nodes

---

## Verbindungsübersicht

```
Internet/Management
    ↓
Router/VPN/DHCP
    ↓
VLAN30 (Mgmt)
    ↓
Managed 10/25GbE Switch
    ├─→ VLAN10 (Cluster) → Mac Studio M3 (10.10.10.11)
    ├─→ VLAN20 (Storage) → NAS (10.20.20.100)
    └─→ VLAN30 (Mgmt) → Mac Studio M4 (10.10.10.12)
```

---

## Technische Details

### Netzwerkkomponenten

- **Switch:** Managed 10/25GbE Switch
- **Storage:** NAS mit 10GbE Anbindung
- **Compute Nodes:** 
  - Mac Studio M3 (Cluster VLAN)
  - Mac Studio M4 (Management VLAN)

### IP-Adressierung

- **Cluster:** 10.10.10.x
- **Storage:** 10.20.20.x
- **Management:** 10.30.30.x (implizit)

---

## Ende

Vielen Dank für Ihre Aufmerksamkeit!

