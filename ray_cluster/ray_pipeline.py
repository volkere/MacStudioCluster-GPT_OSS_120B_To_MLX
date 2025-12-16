"""
Ray-basierte Pipeline für verteilte Face Tagging Verarbeitung
Nutzt Ray für GPU-Ressourcen-Sharing über mehrere Mac Nodes
"""

import ray
import logging
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .ray_face_detection import (
    detect_faces_remote,
    detect_faces_batch_remote,
    crop_face_remote,
    FaceDetectionActor
)
from .ray_embeddings import (
    generate_embedding_remote,
    generate_embeddings_batch_remote,
    EmbeddingActor
)

logger = logging.getLogger(__name__)


class RayFaceTagPipeline:
    """Ray-basierte Pipeline für verteilte Face Tagging Verarbeitung"""
    
    def __init__(self, config_path: Optional[str] = None, ray_address: Optional[str] = None):
        """
        Initialisiert Ray Pipeline
        
        Args:
            config_path: Pfad zur config.yaml
            ray_address: Ray Cluster Address (z.B. "ray://head-node:10001")
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "pipeline" / "config.yaml"
        
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Ray initialisieren
        if ray_address:
            ray.init(address=ray_address, ignore_reinit_error=True)
        else:
            # Lokaler Ray Cluster
            ray.init(
                num_cpus=self.config.get("ray", {}).get("num_cpus", 16),
                num_gpus=self.config.get("ray", {}).get("num_gpus", 1),
                object_store_memory=self.config.get("ray", {}).get("object_store_memory", 32_000_000_000),
                ignore_reinit_error=True
            )
        
        # Ray Actors für persistente Modelle erstellen
        self.face_detection_actors = self._create_face_detection_actors()
        self.embedding_actors = self._create_embedding_actors()
        
        # Logging konfigurieren
        self._setup_logging()
        
        logger.info("Ray Face Tagging Pipeline initialisiert")
        logger.info(f"Ray Cluster: {ray.cluster_resources()}")
    
    def _create_face_detection_actors(self) -> List[Any]:
        """Erstellt Face Detection Actors auf verschiedenen Nodes"""
        num_actors = 2  # Anzahl der Actors (kann an Cluster-Größe angepasst werden)
        actors = []
        
        for i in range(num_actors):
            actor = FaceDetectionActor.remote()
            actors.append(actor)
            logger.info(f"Face Detection Actor {i} erstellt")
        
        return actors
    
    def _create_embedding_actors(self) -> List[Any]:
        """Erstellt Embedding Actors auf verschiedenen Nodes"""
        num_actors = 2  # Anzahl der Actors
        actors = []
        
        for i in range(num_actors):
            actor = EmbeddingActor.remote()
            actors.append(actor)
            logger.info(f"Embedding Actor {i} erstellt")
        
        return actors
    
    def _setup_logging(self):
        """Konfiguriert Logging"""
        log_config = self.config.get("logging", {})
        level = getattr(logging, log_config.get("level", "INFO"))
        
        logging.basicConfig(
            level=level,
            format=log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            handlers=[
                logging.FileHandler(log_config.get("file", "ray_pipeline.log")),
                logging.StreamHandler()
            ]
        )
    
    def _get_face_detection_actor(self) -> Any:
        """Gibt einen verfügbaren Face Detection Actor zurück (Round-Robin)"""
        import random
        return random.choice(self.face_detection_actors)
    
    def _get_embedding_actor(self) -> Any:
        """Gibt einen verfügbaren Embedding Actor zurück (Round-Robin)"""
        import random
        return random.choice(self.embedding_actors)
    
    def process_photo_distributed(self, image_path: str) -> Dict[str, Any]:
        """
        Verarbeitet ein Foto mit verteilter Ray-Verarbeitung
        
        Args:
            image_path: Pfad zur Bilddatei
            
        Returns:
            Dictionary mit Verarbeitungsergebnissen
        """
        photo_id = str(uuid.uuid4())
        logger.info(f"Starte verteilte Verarbeitung von '{image_path}' (Photo-ID: {photo_id})")
        
        result = {
            "photo_id": photo_id,
            "image_path": image_path,
            "timestamp": datetime.now().isoformat(),
            "faces": [],
            "embeddings": [],
            "errors": []
        }
        
        try:
            # Bild laden
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            
            # 1. Face Detection (verteilt über Ray)
            logger.info("Schritt 1: Face Detection (Ray)")
            face_detection_actor = self._get_face_detection_actor()
            faces_future = face_detection_actor.detect.remote(image_bytes)
            faces = ray.get(faces_future)
            result["faces"] = faces
            
            if not faces:
                logger.warning("Keine Gesichter erkannt")
                return result
            
            # 2. Face Crops erstellen (verteilt)
            logger.info(f"Schritt 2: Erstelle {len(faces)} Face Crops (Ray)")
            crop_futures = []
            for i, face in enumerate(faces):
                crop_future = crop_face_remote.remote(
                    image_bytes,
                    face.get("box", [0, 0, 100, 100])
                )
                crop_futures.append(crop_future)
            
            face_crops = ray.get(crop_futures)
            
            # 3. Embeddings generieren (verteilt)
            logger.info("Schritt 3: Embedding-Generierung (Ray)")
            embedding_actor = self._get_embedding_actor()
            embeddings_future = embedding_actor.encode_batch.remote(face_crops)
            embeddings = ray.get(embeddings_future)
            result["embeddings"] = embeddings
            
            # Embeddings zu Faces hinzufügen
            for i, embedding in enumerate(embeddings):
                if i < len(faces):
                    faces[i]["embedding"] = embedding
            
            logger.info(f"Verarbeitung abgeschlossen: {len(faces)} Gesichter, {len(embeddings)} Embeddings")
            
        except Exception as e:
            logger.error(f"Fehler bei verteilter Verarbeitung: {e}", exc_info=True)
            result["errors"].append(str(e))
        
        return result
    
    def process_batch_distributed(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Verarbeitet mehrere Fotos parallel mit Ray
        
        Args:
            image_paths: Liste von Bildpfaden
            
        Returns:
            Liste von Verarbeitungsergebnissen
        """
        logger.info(f"Starte verteilte Batch-Verarbeitung von {len(image_paths)} Bildern")
        
        # Erstelle Futures für alle Bilder
        futures = []
        for image_path in image_paths:
            future = self._process_photo_async(image_path)
            futures.append(future)
        
        # Warte auf alle Ergebnisse
        results = ray.get(futures)
        
        logger.info(f"Batch-Verarbeitung abgeschlossen: {len(results)} Bilder verarbeitet")
        return results
    
    def _process_photo_async(self, image_path: str):
        """Asynchrone Verarbeitung eines Fotos (für Batch-Processing)"""
        @ray.remote
        def process_single():
            return self.process_photo_distributed(image_path)
        
        return process_single.remote()
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Gibt Status des Ray Clusters zurück"""
        return {
            "cluster_resources": ray.cluster_resources(),
            "available_resources": ray.available_resources(),
            "nodes": len(ray.nodes()),
            "actors": {
                "face_detection": len(self.face_detection_actors),
                "embedding": len(self.embedding_actors)
            }
        }
    
    def shutdown(self):
        """Shutdown Ray Cluster"""
        ray.shutdown()
        logger.info("Ray Cluster heruntergefahren")


if __name__ == "__main__":
    # Beispiel-Verwendung
    pipeline = RayFaceTagPipeline()
    
    try:
        # Cluster-Status
        status = pipeline.get_cluster_status()
        print("Ray Cluster Status:")
        print(f"  Nodes: {status['nodes']}")
        print(f"  Resources: {status['cluster_resources']}")
        
        # Beispiel-Verarbeitung
        # result = pipeline.process_photo_distributed("/path/to/image.jpg")
        # print(f"Verarbeitet: {result['photo_id']}")
        
    finally:
        pipeline.shutdown()


