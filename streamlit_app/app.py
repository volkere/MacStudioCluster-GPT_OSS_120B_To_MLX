#!/usr/bin/env python3
"""
Streamlit GUI für Face Tagging Pipeline
Benutzerfreundliche Oberfläche für Bild-Verwaltung und -Verarbeitung
"""

import streamlit as st
import sys
from pathlib import Path
import json
import time
from typing import Dict, Any, List
import io
from PIL import Image
import base64

# Projekt-Root zum Path hinzufügen
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Prüfe Dependencies
try:
    import minio
    import neo4j
    import yaml
except ImportError as e:
    st.error(f"Fehlende Dependencies: {e}")
    st.info("Bitte installieren Sie die Dependencies mit: pip install minio neo4j pyyaml")
    st.stop()

# Lazy Import der Pipeline (nur wenn benötigt)
try:
    from pipeline.face_tag_pipeline import FaceTagPipeline
    from pipeline.minio_client import MinIOClient
except ImportError as e:
    st.error(f"Fehler beim Import der Pipeline: {e}")
    st.info("Bitte stellen Sie sicher, dass alle Dependencies installiert sind:")
    st.code("pip install -e .")
    st.stop()

# Page Config
st.set_page_config(
    page_title="Face Tagging Pipeline - Admin",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS für besseres Styling (ohne Farben)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .step-box {
        border: 2px solid;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .step-completed {
        border-style: solid;
    }
    .step-active {
        border-style: dashed;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .status-online {
        border: 1px solid;
    }
    .status-offline {
        border: 1px solid;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_pipeline():
    """Initialisiert die Pipeline (cached)"""
    try:
        # Prüfe ob Dependencies verfügbar sind
        import minio
        import neo4j
        
        config_path = PROJECT_ROOT / "pipeline" / "config.yaml"
        if not config_path.exists():
            return None, f"Konfigurationsdatei nicht gefunden: {config_path}"
        
        pipeline = FaceTagPipeline(str(config_path))
        return pipeline, None
    except ImportError as e:
        return None, f"Fehlende Dependencies: {e}. Bitte installieren Sie: pip install minio neo4j"
    except Exception as e:
        return None, str(e)


def check_services_status() -> Dict[str, bool]:
    """Prüft Status aller Services"""
    import requests
    
    services = {
        "Face Detection": "http://localhost:5001/health",
        "Embedding": "http://localhost:5002/health",
        "LLM": "http://localhost:8000/v1/models",
        "minIO": "http://localhost:9000/minio/health/live"
    }
    
    status = {}
    for name, url in services.items():
        try:
            if name == "LLM":
                response = requests.get(url, timeout=2)
            else:
                response = requests.get(url, timeout=2)
            status[name] = response.status_code == 200
        except:
            status[name] = False
    
    return status


def display_step(step_num: int, title: str, description: str, status: str = "pending"):
    """Zeigt einen Schritt an"""
    status_class = {
        "completed": "step-completed",
        "active": "step-active",
        "pending": ""
    }.get(status, "")
    
    st.markdown(f"""
    <div class="step-box {status_class}">
        <h3>Schritt {step_num}: {title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<div class="main-header">Face Tagging Pipeline - Admin</div>', unsafe_allow_html=True)
    
    # Sidebar: Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Seite wählen",
        ["Übersicht", "Bild hochladen", "Verarbeitung", "Ergebnisse", "Konfiguration"]
    )
    
    # Services Status
    st.sidebar.markdown("---")
    st.sidebar.subheader("Service-Status")
    services_status = check_services_status()
    
    for service, is_online in services_status.items():
        status_class = "status-online" if is_online else "status-offline"
        status_text = "Online" if is_online else "Offline"
        st.sidebar.markdown(
            f'<span class="status-badge {status_class}">{service}: {status_text}</span>',
            unsafe_allow_html=True
        )
    
    # Hauptinhalt basierend auf ausgewählter Seite
    if page == "Übersicht":
        show_overview()
    elif page == "Bild hochladen":
        show_upload()
    elif page == "Verarbeitung":
        show_processing()
    elif page == "Ergebnisse":
        show_results()
    elif page == "Konfiguration":
        show_configuration()


def show_overview():
    """Übersichtsseite mit Schritt-für-Schritt-Anleitung"""
    st.header("Willkommen zur Face Tagging Pipeline")
    st.markdown("""
    Diese Anwendung führt Sie durch den kompletten Prozess der Gesichts-Erkennung und -Tagging.
    Folgen Sie den Schritten unten, um Bilder zu verarbeiten.
    """)
    
    st.markdown("---")
    st.subheader("Schritt-für-Schritt-Anleitung")
    
    # Schritt 1: Services prüfen
    services_status = check_services_status()
    all_online = all(services_status.values())
    step1_status = "completed" if all_online else "active" if any(services_status.values()) else "pending"
    
    display_step(
        1,
        "Services prüfen",
        "Stellen Sie sicher, dass alle Services laufen (siehe Sidebar). Falls nicht, starten Sie sie mit: ./services/start_services.sh",
        step1_status
    )
    
    if not all_online:
        st.warning("Nicht alle Services sind online. Bitte starten Sie die fehlenden Services.")
        if st.button("Services-Status aktualisieren"):
            st.rerun()
    
    # Schritt 2: Bild hochladen
    step2_status = "pending"
    if all_online:
        step2_status = "active"
    
    display_step(
        2,
        "Bild hochladen",
        "Gehen Sie zur Seite 'Bild hochladen' und wählen Sie ein Bild aus, das verarbeitet werden soll.",
        step2_status
    )
    
    # Schritt 3: Verarbeitung starten
    display_step(
        3,
        "Verarbeitung starten",
        "Gehen Sie zur Seite 'Verarbeitung' und starten Sie die Pipeline für Ihr Bild.",
        "pending"
    )
    
    # Schritt 4: Ergebnisse ansehen
    display_step(
        4,
        "Ergebnisse ansehen",
        "Gehen Sie zur Seite 'Ergebnisse', um die erkannten Gesichter, Cluster und Annotationen zu sehen.",
        "pending"
    )
    
    # Quick Actions
    st.markdown("---")
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Zum Bild-Upload", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()
    
    with col2:
        if st.button("Zur Verarbeitung", use_container_width=True):
            st.session_state.page = "processing"
            st.rerun()
    
    with col3:
        if st.button("Zu den Ergebnissen", use_container_width=True):
            st.session_state.page = "results"
            st.rerun()


def show_upload():
    """Bild-Upload-Seite"""
    st.header("Bild hochladen")
    
    st.markdown("""
    Laden Sie hier ein Bild hoch, das verarbeitet werden soll.
    Unterstützte Formate: JPG, PNG, TIFF, BMP
    """)
    
    # Upload-Widget
    uploaded_file = st.file_uploader(
        "Wählen Sie ein Bild aus",
        type=['jpg', 'jpeg', 'png', 'tiff', 'bmp'],
        help="Wählen Sie ein Bild aus, das Gesichter enthalten soll"
    )
    
    if uploaded_file is not None:
        # Bild anzeigen
        image = Image.open(uploaded_file)
        st.image(image, caption="Hochgeladenes Bild", use_container_width=True)
        
        # Bild-Informationen
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Breite", f"{image.width} px")
        with col2:
            st.metric("Höhe", f"{image.height} px")
        with col3:
            st.metric("Format", image.format)
        
        # Bild speichern
        if 'uploaded_image_path' not in st.session_state:
            # Temporäres Verzeichnis erstellen
            temp_dir = PROJECT_ROOT / "temp_uploads"
            temp_dir.mkdir(exist_ok=True)
            
            # Bild speichern
            image_path = temp_dir / uploaded_file.name
            image.save(image_path)
            st.session_state.uploaded_image_path = str(image_path)
            st.session_state.uploaded_image = image
        
        st.success(f"Bild gespeichert: {uploaded_file.name}")
        
        # Weiter zur Verarbeitung
        st.markdown("---")
        st.info("**Nächster Schritt:** Gehen Sie zur Seite 'Verarbeitung', um das Bild zu verarbeiten.")
        
        if st.button("Jetzt verarbeiten", type="primary", use_container_width=True):
            st.session_state.page = "processing"
            st.rerun()


def show_processing():
    """Verarbeitungs-Seite"""
    st.header("Bild-Verarbeitung")
    
    # Prüfe ob Bild hochgeladen wurde
    if 'uploaded_image_path' not in st.session_state:
        st.warning("Bitte laden Sie zuerst ein Bild hoch (Seite 'Bild hochladen').")
        if st.button("Zum Bild-Upload"):
            st.session_state.page = "upload"
            st.rerun()
        return
    
    # Zeige Bild
    if 'uploaded_image' in st.session_state:
        st.image(st.session_state.uploaded_image, caption="Zu verarbeitendes Bild", use_container_width=True)
    
    st.markdown(f"**Bild:** {Path(st.session_state.uploaded_image_path).name}")
    
    # Verarbeitungs-Optionen
    st.markdown("---")
    st.subheader("Verarbeitungs-Optionen")
    
    col1, col2 = st.columns(2)
    with col1:
        upload_to_minio = st.checkbox("Zu minIO hochladen", value=True, help="Bild wird zu minIO hochgeladen")
    with col2:
        use_ray = st.checkbox("Ray Cluster nutzen", value=False, help="Verteilte Verarbeitung über Ray Cluster")
    
    # Verarbeitung starten
    st.markdown("---")
    
    if st.button("Verarbeitung starten", type="primary", use_container_width=True):
        # Pipeline initialisieren
        pipeline, error = init_pipeline()
        
        if error:
            st.error(f"Fehler beim Initialisieren der Pipeline: {error}")
            return
        
        # Progress Bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Schritt 1: Face Detection
            status_text.text("Schritt 1/6: Gesichter erkennen...")
            progress_bar.progress(16)
            time.sleep(0.5)
            
            # Schritt 2: Face Cropping
            status_text.text("Schritt 2/6: Gesichter ausschneiden...")
            progress_bar.progress(33)
            time.sleep(0.5)
            
            # Schritt 3: Embeddings generieren
            status_text.text("Schritt 3/6: Embeddings generieren...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            # Schritt 4: Clustering
            status_text.text("Schritt 4/6: Ähnliche Gesichter gruppieren...")
            progress_bar.progress(66)
            time.sleep(0.5)
            
            # Schritt 5: LLM-Annotation
            status_text.text("Schritt 5/6: Namen und Events generieren...")
            progress_bar.progress(83)
            time.sleep(0.5)
            
            # Schritt 6: Neo4j-Speicherung
            status_text.text("Schritt 6/6: Daten speichern...")
            progress_bar.progress(100)
            
            # Eigentliche Verarbeitung
            with st.spinner("Verarbeite Bild..."):
                result = pipeline.process_photo(
                    st.session_state.uploaded_image_path,
                    upload_to_minio=upload_to_minio
                )
            
            # Ergebnis speichern
            st.session_state.last_result = result
            st.session_state.processing_complete = True
            
            status_text.text("Verarbeitung abgeschlossen!")
            st.success("Bild erfolgreich verarbeitet!")
            
            # Zusammenfassung
            st.markdown("---")
            st.subheader("Verarbeitungs-Zusammenfassung")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gesichter erkannt", len(result.get('faces', [])))
            with col2:
                st.metric("Cluster erstellt", len(result.get('clusters', [])))
            with col3:
                st.metric("Fehler", len(result.get('errors', [])))
            
            # Weiter zu Ergebnissen
            st.markdown("---")
            st.info("**Nächster Schritt:** Gehen Sie zur Seite 'Ergebnisse', um Details zu sehen.")
            
            if st.button("Ergebnisse anzeigen", type="primary", use_container_width=True):
                st.session_state.page = "results"
                st.rerun()
                
        except Exception as e:
            st.error(f"Fehler bei der Verarbeitung: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
        finally:
            progress_bar.empty()
            status_text.empty()


def show_results():
    """Ergebnis-Anzeige"""
    st.header("Verarbeitungs-Ergebnisse")
    
    if 'last_result' not in st.session_state:
        st.warning("Keine Ergebnisse verfügbar. Bitte verarbeiten Sie zuerst ein Bild.")
        if st.button("Zur Verarbeitung"):
            st.session_state.page = "processing"
            st.rerun()
        return
    
    result = st.session_state.last_result
    
    # Übersicht
    st.subheader("Übersicht")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Photo-ID", result['photo_id'][:8] + "...")
    with col2:
        st.metric("Gesichter", len(result.get('faces', [])))
    with col3:
        st.metric("Cluster", len(result.get('clusters', [])))
    with col4:
        st.metric("Zeitstempel", result.get('timestamp', 'N/A')[:10])
    
    # Gesichter
    st.markdown("---")
    st.subheader("Erkannte Gesichter")
    
    faces = result.get('faces', [])
    if faces:
        for i, face in enumerate(faces):
            with st.expander(f"Gesicht {i+1} - Confidence: {face.get('confidence', 0):.2%}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.json({
                        "Bounding Box": face.get('box'),
                        "Confidence": face.get('confidence'),
                        "Cluster ID": face.get('cluster_id')
                    })
                with col2:
                    if face.get('crop_path'):
                        st.info(f"Crop-Pfad: {face['crop_path']}")
    else:
        st.info("Keine Gesichter erkannt.")
    
    # Cluster
    st.markdown("---")
    st.subheader("Gesichts-Cluster")
    
    clusters = result.get('clusters', [])
    if clusters:
        for cluster in clusters:
            with st.expander(f"Cluster {cluster.get('cluster_id')}: {cluster.get('name', 'Unbekannt')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Anzahl Gesichter", cluster.get('n_faces', 0))
                    st.json({
                        "Cluster ID": cluster.get('cluster_id'),
                        "Name": cluster.get('name'),
                        "Event Info": cluster.get('event_info', {})
                    })
                with col2:
                    if cluster.get('representative_face'):
                        st.info(f"Repräsentatives Gesicht: {cluster['representative_face']}")
    else:
        st.info("Keine Cluster erstellt.")
    
    # Fehler
    errors = result.get('errors', [])
    if errors:
        st.markdown("---")
        st.subheader("Fehler")
        for error in errors:
            st.error(error)
    
    # JSON-Export
    st.markdown("---")
    st.subheader("Export")
    
    json_str = json.dumps(result, indent=2, ensure_ascii=False)
    st.download_button(
        label="Ergebnis als JSON herunterladen",
        data=json_str,
        file_name=f"result_{result['photo_id']}.json",
        mime="application/json"
    )
    
    # JSON anzeigen
    with st.expander("Vollständiges JSON anzeigen"):
        st.code(json_str, language="json")


def show_configuration():
    """Konfigurations-Seite"""
    st.header("⚙️ Konfiguration")
    
    config_path = PROJECT_ROOT / "pipeline" / "config.yaml"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        st.subheader("Aktuelle Konfiguration")
        
        # Service-Endpoints
        st.markdown("### Service-Endpoints")
        services = config.get('services', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Face Detection URL", value=services.get('face_detection', {}).get('url', ''))
            st.text_input("Embedding URL", value=services.get('embedding', {}).get('url', ''))
        with col2:
            st.text_input("LLM URL", value=services.get('llm', {}).get('url', ''))
        
        # minIO
        st.markdown("### minIO Konfiguration")
        minio_config = config.get('minio', {})
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("minIO Endpoint", value=minio_config.get('endpoint', ''))
        with col2:
            st.text_input("Access Key", value=minio_config.get('access_key', ''), type="password")
        
        # Neo4j
        st.markdown("### Neo4j Konfiguration")
        neo4j_config = config.get('neo4j', {})
        st.text_input("Neo4j URI", value=neo4j_config.get('uri', ''))
        
        st.info("Um die Konfiguration zu ändern, bearbeiten Sie die Datei: pipeline/config.yaml")
    else:
        st.error("Konfigurationsdatei nicht gefunden!")


if __name__ == "__main__":
    main()
