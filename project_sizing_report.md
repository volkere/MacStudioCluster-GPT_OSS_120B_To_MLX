# Project Sizing Report
## Face Tagging Projekt - 400.000 digitale Fotos

**Erstellt:** 2025  
**Projektumfang:** 400.000 digitale Fotos  
**Ziel:** Vollständige Annotation mit Face Detection, Clustering und KI-gestützter Annotation

---

## Executive Summary

Dieser Report schätzt die Ressourcen, Zeit und Kosten für ein Face-Tagging-Projekt mit 400.000 digitalen Fotos. Das System nutzt einen Mac Studio Cluster mit KI-gestützter Annotation (GPT-OSS-120B) und Graph-Datenbank (Neo4j).

**Kernannahmen:**
- Durchschnittlich 2,5 Gesichter pro Foto
- 1.000.000 Gesichter insgesamt
- Durchschnittliche Bildgröße: 5 MB (JPEG)
- 80% der Fotos enthalten Gesichter

---

## 1. Datenvolumen & Speicherbedarf

### 1.1 Rohdaten

| Komponente | Menge | Größe pro Einheit | Gesamt |
|------------|-------|-------------------|--------|
| Originale Fotos | 400.000 | 5 MB | **2.000 GB (2 TB)** |
| Backup/Rohdaten | 400.000 | 5 MB | **2.000 GB (2 TB)** |

**Gesamt Rohdaten: 4 TB**

### 1.2 Verarbeitete Daten

| Komponente | Menge | Größe pro Einheit | Gesamt |
|------------|-------|-------------------|--------|
| Processed Images | 400.000 | 5 MB | **2.000 GB (2 TB)** |
| Face Crops | 1.000.000 | 0,1 MB | **100 GB** |
| Detection JSON | 400.000 | 0,05 MB | **20 GB** |
| Embedding Vectors | 1.000.000 | 0,01 MB | **10 GB** |
| Annotation JSON | 400.000 | 0,1 MB | **40 GB** |
| Neo4j Datenbank | - | - | **200 GB** (geschätzt) |
| GPT-Output/Cache | - | - | **50 GB** |

**Gesamt verarbeitete Daten: ~2.420 GB (2,4 TB)**

### 1.3 Gesamtspeicherbedarf

| Phase | Speicherbedarf |
|-------|----------------|
| Rohdaten (inkl. Backup) | 4 TB |
| Verarbeitete Daten | 2,4 TB |
| Working Space (20% Overhead) | 1,3 TB |
| **Gesamt (inkl. Redundanz)** | **~8 TB** |

**Empfehlung:** 10 TB NAS Storage (10GbE) für ausreichenden Puffer

---

## 2. Hardware-Anforderungen

### 2.1 Compute Nodes (basierend auf Mac Studio Cluster)

#### Mac Studio M3 (Cluster Node - Hauptverarbeitung)
- **Anzahl:** 2-3 Nodes empfohlen
- **CPU:** M3 Max (16-Core CPU)
- **GPU:** M3 Max (40-Core GPU)
- **RAM:** 128 GB pro Node
- **Aufgabe:** Face Detection, Embedding-Generierung, Clustering

#### Mac Studio M4 (Management Node)
- **Anzahl:** 1 Node
- **CPU:** M4 Max
- **RAM:** 128 GB
- **Aufgabe:** GPT-OSS-120B, Neo4j, Backend-Services

### 2.2 Storage

- **NAS:** 10 TB Kapazität, 10GbE Anbindung
- **Lokaler Cache:** 2 TB SSD pro Compute Node

### 2.3 Netzwerk

- **Switch:** Managed 10/25GbE Switch
- **VLAN-Struktur:** VLAN10 (Cluster), VLAN20 (Storage), VLAN30 (Management)

---

## 3. Verarbeitungszeit & Durchsatz

### 3.1 Verarbeitungsschritte (pro Foto)

| Schritt | Zeit pro Foto | Zeit pro Gesicht | Parallelisierbar |
|---------|---------------|------------------|------------------|
| Upload zu minIO | 0,5 s | - | Ja |
| Face Detection | 1,5 s | - | Ja |
| Embedding-Generierung | - | 0,3 s | Ja |
| Clustering (Batch) | 0,1 s | - | Nein |
| GPT-Annotation | 10 s | - | Teilweise |
| Neo4j Speicherung | 0,2 s | - | Ja |
| **Gesamt (seriell)** | **~12,3 s** | - | - |

### 3.2 Durchsatz-Berechnung

**Annahmen:**
- 2 Mac Studio M3 Nodes parallel
- 4 parallele Verarbeitungsströme pro Node
- Effizienz: 80% (Overhead, Wartezeiten)

**Durchsatz pro Node:**
- 4 Streams × (3600s / 12,3s) = ~1.170 Fotos/Stunde pro Node
- Bei 80% Effizienz: ~936 Fotos/Stunde pro Node

**Gesamtdurchsatz (2 Nodes):**
- 2 × 936 = **1.872 Fotos/Stunde**
- **~45.000 Fotos/Tag** (24h Betrieb)
- **~315.000 Fotos/Woche** (7 Tage)

### 3.3 Projektzeitrahmen

| Szenario | Fotos/Tag | Tage (400.000 Fotos) | Kalenderwochen |
|----------|-----------|----------------------|----------------|
| 24/7 Betrieb | 45.000 | **9 Tage** | **1,3 Wochen** |
| 12h/Tag Betrieb | 22.500 | **18 Tage** | **2,6 Wochen** |
| 8h/Tag Betrieb | 15.000 | **27 Tage** | **~4 Wochen** |

**Empfehlung:** 3-4 Wochen für vollständige Verarbeitung (inkl. Puffer für Fehlerbehandlung, Optimierungen)

---

## 4. Software-Komponenten & Skalierung

### 4.1 Docker-Services (pro Node)

| Service | CPU | RAM | GPU | Instanzen |
|---------|-----|-----|-----|-----------|
| Face-Service | 4 Core | 8 GB | 1x | 2-4 |
| Embedding-Service | 4 Core | 8 GB | 1x | 2-4 |
| Backend (FastAPI) | 2 Core | 4 GB | - | 1 |
| minIO | 2 Core | 4 GB | - | 1 |
| Neo4j | 4 Core | 16 GB | - | 1 |
| GPT-OSS-120B | 8 Core | 64 GB | - | 1 |
| Streamlit | 1 Core | 2 GB | - | 1 |

**Gesamt pro Node:** ~16 CPU Cores, ~106 GB RAM

### 4.2 Skalierung für 400.000 Fotos

**Optimale Konfiguration:**
- **2-3 Compute Nodes** für Face Detection & Embeddings
- **1 Management Node** für GPT-OSS-120B und Neo4j
- **1 Storage Node** (NAS)

---

## 5. Kosten-Schätzung

### 5.1 Hardware (Einmalkosten)

| Komponente | Anzahl | Preis pro Einheit | Gesamt |
|------------|--------|-------------------|--------|
| Mac Studio M3 Max | 2 | € 5.500 | **€ 11.000** |
| Mac Studio M4 Max | 1 | € 6.000 | **€ 6.000** |
| NAS (10 TB, 10GbE) | 1 | € 1.500 | **€ 1.500** |
| Managed Switch (10/25GbE) | 1 | € 800 | **€ 800** |
| Netzwerk-Kabel, Zubehör | - | - | **€ 500** |
| **Hardware gesamt** | | | **€ 19.800** |

### 5.2 Software & Lizenzen

| Komponente | Kosten |
|------------|--------|
| Neo4j Community (kostenlos) | € 0 |
| minIO (Open Source) | € 0 |
| GPT-OSS-120B (Open Source) | € 0 |
| InsightFace/RetinaFace (Open Source) | € 0 |
| Docker (kostenlos) | € 0 |
| **Software gesamt** | **€ 0** |

### 5.3 Betriebskosten (3 Monate Projekt)

| Komponente | Kosten/Monat | 3 Monate |
|------------|--------------|----------|
| Strom (3 Nodes, 24/7) | € 150 | **€ 450** |
| Internet/Netzwerk | € 50 | **€ 150** |
| Wartung/Support | € 200 | **€ 600** |
| **Betrieb gesamt** | | **€ 1.200** |

### 5.4 Personal (optional)

| Rolle | Stunden/Tag | Tage | Stundensatz | Gesamt |
|-------|-------------|------|-------------|--------|
| DevOps Engineer (Setup) | 8 | 5 | € 80 | **€ 3.200** |
| Data Engineer (Monitoring) | 4 | 20 | € 70 | **€ 5.600** |
| Annotation Reviewer | 8 | 15 | € 50 | **€ 6.000** |
| **Personal gesamt** | | | | **€ 14.800** |

### 5.5 Gesamtkosten

| Kategorie | Kosten |
|-----------|--------|
| Hardware (Einmal) | € 19.800 |
| Software | € 0 |
| Betrieb (3 Monate) | € 1.200 |
| Personal (optional) | € 14.800 |
| **Gesamt** | **€ 35.800** |

**Ohne Personal:** € 21.000

---

## 6. Risiken & Herausforderungen

### 6.1 Technische Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| GPT-OSS-120B Performance | Mittel | Hoch | Alternative Modelle testen, Batch-Processing |
| Neo4j Skalierung | Niedrig | Mittel | Index-Optimierung, Sharding |
| Storage-Engpass | Niedrig | Mittel | 10GbE Netzwerk, lokaler Cache |
| Face Detection Fehlerrate | Mittel | Mittel | Mehrere Modelle parallel, Manual Review |

### 6.2 Projektrisiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Verzögerungen durch Bugs | Mittel | Mittel | Pufferzeit einplanen, Testphase |
| Unerwartete Datenqualität | Hoch | Mittel | Stichproben-Analyse vor Start |
| Hardware-Ausfälle | Niedrig | Hoch | Redundanz, Backup-Strategie |

---

## 7. Optimierungsmöglichkeiten

### 7.1 Performance-Optimierung

- **Batch-Processing:** Clustering in Batches von 10.000 Gesichtern
- **GPU-Beschleunigung:** Face Detection und Embeddings auf GPU
- **Caching:** Häufige Queries cachen
- **Parallelisierung:** Mehrere Streams pro Node

### 7.2 Kosten-Optimierung

- **Cloud-Alternative:** AWS/GCP für temporäre Skalierung
- **Shared Resources:** Hardware nach Projekt wiederverwenden
- **Open Source:** Alle Software-Komponenten kostenlos

---

## 8. Phasenplan

### Phase 1: Setup & Testing (Woche 1-2)
- Hardware-Aufbau
- Software-Installation
- Test mit 1.000 Fotos
- Performance-Tuning

### Phase 2: Pilot-Phase (Woche 3)
- Verarbeitung von 10.000 Fotos
- Qualitätskontrolle
- Anpassungen

### Phase 3: Vollständige Verarbeitung (Woche 4-6)
- 400.000 Fotos verarbeiten
- Monitoring & Fehlerbehandlung
- Kontinuierliche Qualitätskontrolle

### Phase 4: Review & Export (Woche 7-8)
- Manuelle Review kritischer Fälle
- Export der Daten
- Dokumentation

**Gesamtprojektzeit: 8 Wochen**

---

## 9. Erfolgsmetriken

### 9.1 Technische Metriken

- **Face Detection Rate:** >95% (bei vorhandenen Gesichtern)
- **Clustering Accuracy:** >90% (gleiche Person in einem Cluster)
- **Verarbeitungsgeschwindigkeit:** >1.500 Fotos/Stunde
- **System-Uptime:** >95%

### 9.2 Qualitätsmetriken

- **Annotation Accuracy:** >80% (durch GPT-OSS-120B)
- **Manual Review Rate:** <20% der Fotos benötigen Review
- **Datenqualität:** Vollständige Metadaten für alle Fotos

---

## 10. Empfehlungen

### 10.1 Hardware

**Empfohlen:**
- 2-3 Mac Studio M3 Max für Compute
- 1 Mac Studio M4 Max für Management/GPT
- 10 TB NAS mit 10GbE
- Managed 10/25GbE Switch

### 10.2 Software-Stack

**Empfohlen:**
- RetinaFace für Face Detection (robust bei alten Fotos)
- ArcFace/InsightFace für Embeddings
- DBSCAN für Clustering
- GPT-OSS-120B für Annotation
- Neo4j für Graph-Storage
- Streamlit für Review-UI

### 10.3 Projektmanagement

**Empfohlen:**
- 3-4 Wochen für Verarbeitung einplanen
- Puffer von 20% für unerwartete Probleme
- Regelmäßige Qualitätskontrollen
- Staged Rollout (Pilot → Vollbetrieb)

---

## 11. Zusammenfassung

| Metrik | Wert |
|--------|------|
| **Fotos** | 400.000 |
| **Gesichter (geschätzt)** | 1.000.000 |
| **Speicherbedarf** | ~8 TB |
| **Verarbeitungszeit** | 3-4 Wochen |
| **Hardware-Kosten** | € 19.800 |
| **Gesamtkosten (mit Personal)** | € 35.800 |
| **Durchsatz** | ~1.872 Fotos/Stunde |
| **Compute Nodes** | 2-3 Mac Studio M3 |
| **Management Node** | 1 Mac Studio M4 |

---

**Report erstellt basierend auf:**
- Hardware-Spezifikationen (Mac Studio Cluster)
- Software-Architektur (Face Tag Software)
- Typische Performance-Metriken für Face Detection & Embedding
- Erfahrungswerte für KI-gestützte Annotation

**Nächste Schritte:**
1. Hardware-Beschaffung
2. Proof-of-Concept mit 1.000 Fotos
3. Performance-Tuning
4. Vollständige Verarbeitung

---

*Ende des Reports*

