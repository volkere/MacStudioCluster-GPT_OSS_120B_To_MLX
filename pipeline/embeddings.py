"""
Embedding Service Integration (ArcFace/MLX-optimiert)
"""

import logging
import requests
import time
from typing import List, Dict, Any, Optional
import base64

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Client für Embedding Service (MLX-optimiert)"""
    
    def __init__(self, config: dict):
        """
        Initialisiert Embedding Service Client
        
        Args:
            config: Konfiguration aus config.yaml
        """
        service_config = config.get("services", {}).get("embedding", {})
        self.url = service_config.get("url", "http://localhost:5002")
        self.timeout = service_config.get("timeout", 30)
        self.retry_attempts = service_config.get("retry_attempts", 3)
    
    def _encode_image_bytes(self, image_bytes: bytes) -> str:
        """Kodiert Bilddaten als Base64-String"""
        return base64.b64encode(image_bytes).decode("utf-8")
    
    def get_embedding(self, face_crop_bytes: bytes) -> List[float]:
        """
        Generiert Embedding für ein Gesichts-Crop
        
        Args:
            face_crop_bytes: Gesichts-Crop als Bytes
            
        Returns:
            Embedding-Vektor als Liste von Floats
        """
        image_data = self._encode_image_bytes(face_crop_bytes)
        
        payload = {
            "image": image_data,
            "normalize": True
        }
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    f"{self.url}/embed",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                embedding = result.get("embedding", [])
                confidence = result.get("confidence", 0.0)
                
                logger.debug(f"Embedding generiert (Dimension: {len(embedding)}, Confidence: {confidence:.3f})")
                return embedding
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Versuch {attempt + 1}/{self.retry_attempts} fehlgeschlagen: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Embedding-Generierung nach {self.retry_attempts} Versuchen fehlgeschlagen")
                    raise
    
    def get_embeddings_batch(self, face_crops: List[bytes]) -> List[List[float]]:
        """
        Generiert Embeddings für mehrere Gesichts-Crops (Batch-Processing)
        
        Args:
            face_crops: Liste von Gesichts-Crops als Bytes
            
        Returns:
            Liste von Embedding-Vektoren
        """
        embeddings = []
        
        for i, crop in enumerate(face_crops):
            try:
                embedding = self.get_embedding(crop)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Fehler bei Embedding-Generierung für Crop {i}: {e}")
                embeddings.append([])  # Leeres Embedding bei Fehler
        
        return embeddings
    
    def get_embeddings_batch_api(self, face_crops: List[bytes]) -> List[List[float]]:
        """
        Generiert Embeddings für mehrere Gesichts-Crops über Batch-API (effizienter)
        
        Args:
            face_crops: Liste von Gesichts-Crops als Bytes
            
        Returns:
            Liste von Embedding-Vektoren
        """
        images_data = [self._encode_image_bytes(crop) for crop in face_crops]
        
        payload = {
            "images": images_data,
            "normalize": True
        }
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    f"{self.url}/embed/batch",
                    json=payload,
                    timeout=self.timeout * len(face_crops)  # Mehr Zeit für Batch
                )
                response.raise_for_status()
                
                result = response.json()
                embeddings = result.get("embeddings", [])
                
                logger.info(f"{len(embeddings)} Embeddings generiert (Batch)")
                return embeddings
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Versuch {attempt + 1}/{self.retry_attempts} fehlgeschlagen: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Batch-Embedding-Generierung nach {self.retry_attempts} Versuchen fehlgeschlagen")
                    # Fallback zu einzelnen Requests
                    return self.get_embeddings_batch(face_crops)
