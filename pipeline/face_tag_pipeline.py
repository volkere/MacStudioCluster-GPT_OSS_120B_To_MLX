"""
Face Tagging Pipeline - End-to-End Verarbeitung
Hauptmodul, das alle Komponenten zusammenführt
"""

import logging
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .minio_client import MinIOClient
from .face_detection import FaceDetectionService
from .embeddings import EmbeddingService
from .clustering import FaceClustering
from .llm_service import LLMService
from .neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)


class FaceTagPipeline:
    """Haupt-Pipeline für Face Tagging"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialisiert die Pipeline
        
        Args:
            config_path: Pfad zur config.yaml (optional)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Services initialisieren
        self.minio = MinIOClient(self.config)
        self.face_detection = FaceDetectionService(self.config)
        self.embeddings = EmbeddingService(self.config)
        self.clustering = FaceClustering(self.config)
        self.llm = LLMService(self.config)
        self.neo4j = Neo4jClient(self.config)
        
        # Logging konfigurieren
        self._setup_logging()
        
        logger.info("Face Tagging Pipeline initialisiert")
    
    def _setup_logging(self):
        """Konfiguriert Logging"""
        log_config = self.config.get("logging", {})
        level = getattr(logging, log_config.get("level", "INFO"))
        
        logging.basicConfig(
            level=level,
            format=log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            handlers=[
                logging.FileHandler(log_config.get("file", "pipeline.log")),
                logging.StreamHandler()
            ]
        )
    
    def process_photo(self, image_path: str, upload_to_minio: bool = True) -> Dict[str, Any]:
        """
        Verarbeitet ein einzelnes Foto durch die komplette Pipeline
        
        Args:
            image_path: Pfad zur Bilddatei
            upload_to_minio: Ob Bild zu minIO hochgeladen werden soll
            
        Returns:
            Dictionary mit Verarbeitungsergebnissen
        """
        photo_id = str(uuid.uuid4())
        logger.info(f"Starte Verarbeitung von '{image_path}' (Photo-ID: {photo_id})")
        
        result = {
            "photo_id": photo_id,
            "image_path": image_path,
            "timestamp": datetime.now().isoformat(),
            "faces": [],
            "clusters": [],
            "errors": []
        }
        
        try:
            # 1. Upload zu minIO (optional)
            if upload_to_minio:
                minio_path = self.minio.upload_image(image_path, "incoming", f"{photo_id}.jpg")
                result["minio_path"] = minio_path
            else:
                result["minio_path"] = image_path
            
            # 2. Face Detection
            logger.info("Schritt 1: Face Detection")
            image_bytes = self.minio.get_image_bytes("incoming", f"{photo_id}.jpg") if upload_to_minio else None
            if image_bytes is None:
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
            
            faces = self.face_detection.detect_faces(image_bytes=image_bytes)
            result["faces"] = faces
            
            if not faces:
                logger.warning("Keine Gesichter erkannt")
                return result
            
            # 3. Face Crops erstellen
            logger.info(f"Schritt 2: Erstelle {len(faces)} Face Crops")
            face_crops = []
            for i, face in enumerate(faces):
                try:
                    crop_bytes = self.face_detection.crop_face(
                        image_bytes,
                        face.get("box", [0, 0, 100, 100])
                    )
                    face_crops.append(crop_bytes)
                    
                    # Crop zu minIO hochladen
                    crop_name = f"{photo_id}_face_{i}.jpg"
                    self.minio.upload_bytes(crop_bytes, "crops", crop_name, "image/jpeg")
                    face["crop_path"] = f"crops/{crop_name}"
                except Exception as e:
                    logger.error(f"Fehler beim Croppen von Gesicht {i}: {e}")
                    result["errors"].append(f"Face crop {i}: {str(e)}")
            
            # 4. Embeddings generieren
            logger.info("Schritt 3: Embedding-Generierung")
            embeddings = self.embeddings.get_embeddings_batch_api(face_crops)
            
            # Embeddings zu Faces hinzufügen
            for i, embedding in enumerate(embeddings):
                if i < len(faces):
                    faces[i]["embedding"] = embedding
            
            # 5. Clustering
            logger.info("Schritt 4: Clustering")
            valid_embeddings = [e for e in embeddings if e]  # Nur gültige Embeddings
            if len(valid_embeddings) > 1:
                labels, cluster_dict = self.clustering.cluster_embeddings(valid_embeddings)
                cluster_stats = self.clustering.get_cluster_statistics(labels, cluster_dict)
                result["cluster_stats"] = cluster_stats
                
                # Cluster-Informationen zu Faces hinzufügen
                embedding_idx = 0
                for i, face in enumerate(faces):
                    if face.get("embedding"):
                        if embedding_idx < len(labels):
                            face["cluster_id"] = int(labels[embedding_idx])
                            embedding_idx += 1
            else:
                logger.info("Zu wenige Embeddings für Clustering")
                labels = []
                cluster_dict = {}
            
            # 6. LLM-Annotation für Cluster
            logger.info("Schritt 5: LLM-Annotation")
            processed_clusters = set()
            for cluster_id, face_indices in cluster_dict.items():
                if cluster_id == -1:  # Noise-Punkte überspringen
                    continue
                if cluster_id in processed_clusters:
                    continue
                
                processed_clusters.add(cluster_id)
                cluster_faces = [faces[i] for i in face_indices if i < len(faces)]
                
                # Cluster-Name mit LLM generieren
                try:
                    cluster_name = self.llm.ask_for_cluster_name(len(cluster_faces))
                    logger.info(f"Cluster {cluster_id}: '{cluster_name}'")
                    
                    # Event-Informationen anreichern
                    image_info = {
                        "photo_id": photo_id,
                        "n_faces": len(cluster_faces),
                        "timestamp": result["timestamp"]
                    }
                    event_info = self.llm.enrich_event_info(cluster_name, image_info)
                    
                    # Neo4j-Integration
                    person_node = self.neo4j.create_person(cluster_name)
                    event_node = self.neo4j.create_event(
                        event_info.get("event_type", "Unknown"),
                        event_info.get("date"),
                        event_info.get("location")
                    )
                    photo_node = self.neo4j.create_photo(photo_id, result.get("minio_path", ""))
                    
                    # Verknüpfungen erstellen
                    if person_node and event_node:
                        self.neo4j.link_person_to_event(cluster_name, event_node.get("id"))
                    if person_node and photo_node:
                        self.neo4j.link_person_to_photo(cluster_name, photo_id)
                    
                    cluster_info = {
                        "cluster_id": cluster_id,
                        "name": cluster_name,
                        "n_faces": len(cluster_faces),
                        "event_info": event_info,
                        "person_node": person_node,
                        "event_node": event_node
                    }
                    result["clusters"].append(cluster_info)
                    
                except Exception as e:
                    logger.error(f"Fehler bei LLM-Annotation für Cluster {cluster_id}: {e}")
                    result["errors"].append(f"Cluster {cluster_id} annotation: {str(e)}")
            
            logger.info(f"Verarbeitung abgeschlossen: {len(result['clusters'])} Cluster erstellt")
            
        except Exception as e:
            logger.error(f"Fehler bei Verarbeitung von '{image_path}': {e}", exc_info=True)
            result["errors"].append(str(e))
        
        return result
    
    def process_batch(self, image_paths: List[str], upload_to_minio: bool = True) -> List[Dict[str, Any]]:
        """
        Verarbeitet mehrere Fotos (Batch-Processing)
        
        Args:
            image_paths: Liste von Bildpfaden
            upload_to_minio: Ob Bilder zu minIO hochgeladen werden sollen
            
        Returns:
            Liste von Verarbeitungsergebnissen
        """
        logger.info(f"Starte Batch-Verarbeitung von {len(image_paths)} Bildern")
        
        results = []
        for i, image_path in enumerate(image_paths, 1):
            logger.info(f"Verarbeite Bild {i}/{len(image_paths)}: {image_path}")
            try:
                result = self.process_photo(image_path, upload_to_minio)
                results.append(result)
            except Exception as e:
                logger.error(f"Fehler bei Verarbeitung von '{image_path}': {e}")
                results.append({
                    "image_path": image_path,
                    "errors": [str(e)]
                })
        
        logger.info(f"Batch-Verarbeitung abgeschlossen: {len(results)} Bilder verarbeitet")
        return results
    
    def process_minio_bucket(self, bucket: str = "incoming") -> List[Dict[str, Any]]:
        """
        Verarbeitet alle Bilder in einem minIO-Bucket
        
        Args:
            bucket: Bucket-Name
            
        Returns:
            Liste von Verarbeitungsergebnissen
        """
        logger.info(f"Verarbeite alle Bilder in Bucket '{bucket}'")
        
        image_paths = self.minio.list_images(bucket)
        logger.info(f"{len(image_paths)} Bilder gefunden")
        
        results = []
        for image_name in image_paths:
            try:
                # Temporäre Datei herunterladen
                temp_path = f"/tmp/{image_name}"
                self.minio.download_image(bucket, image_name, temp_path)
                
                # Verarbeiten
                result = self.process_photo(temp_path, upload_to_minio=False)
                results.append(result)
                
                # Temporäre Datei löschen
                Path(temp_path).unlink()
                
            except Exception as e:
                logger.error(f"Fehler bei Verarbeitung von '{image_name}': {e}")
                results.append({
                    "image_path": image_name,
                    "errors": [str(e)]
                })
        
        return results
    
    def close(self):
        """Schließt alle Verbindungen"""
        self.neo4j.close()
        logger.info("Pipeline geschlossen")


