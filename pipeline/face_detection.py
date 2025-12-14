"""
Face Detection Service Integration (MLX-optimiert)
"""

import logging
import requests
import time
from typing import List, Dict, Any, Optional
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)


class FaceDetectionService:
    """Client für Face Detection Service (MLX-optimiert)"""
    
    def __init__(self, config: dict):
        """
        Initialisiert Face Detection Service Client
        
        Args:
            config: Konfiguration aus config.yaml
        """
        service_config = config.get("services", {}).get("face_detection", {})
        self.url = service_config.get("url", "http://localhost:5001")
        self.timeout = service_config.get("timeout", 30)
        self.retry_attempts = service_config.get("retry_attempts", 3)
    
    def _encode_image(self, image_path: str) -> str:
        """
        Kodiert ein Bild als Base64-String
        
        Args:
            image_path: Pfad zur Bilddatei
            
        Returns:
            Base64-kodierter String
        """
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _encode_image_bytes(self, image_bytes: bytes) -> str:
        """
        Kodiert Bilddaten als Base64-String
        
        Args:
            image_bytes: Bilddaten als Bytes
            
        Returns:
            Base64-kodierter String
        """
        return base64.b64encode(image_bytes).decode("utf-8")
    
    def detect_faces(self, image_path: Optional[str] = None, image_bytes: Optional[bytes] = None) -> List[Dict[str, Any]]:
        """
        Erkennt Gesichter in einem Bild
        
        Args:
            image_path: Pfad zur Bilddatei (optional)
            image_bytes: Bilddaten als Bytes (optional)
            
        Returns:
            Liste von erkannten Gesichtern mit Bounding Boxes und Landmarks
        """
        if image_path:
            image_data = self._encode_image(image_path)
        elif image_bytes:
            image_data = self._encode_image_bytes(image_bytes)
        else:
            raise ValueError("Entweder image_path oder image_bytes muss angegeben werden")
        
        payload = {
            "image": image_data,
            "return_landmarks": True,
            "return_confidence": True
        }
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    f"{self.url}/detect",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                faces = result.get("faces", [])
                
                logger.info(f"{len(faces)} Gesicht(er) erkannt")
                return faces
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Versuch {attempt + 1}/{self.retry_attempts} fehlgeschlagen: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Face Detection nach {self.retry_attempts} Versuchen fehlgeschlagen")
                    raise
    
    def detect_faces_batch(self, image_paths: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Erkennt Gesichter in mehreren Bildern (Batch-Processing)
        
        Args:
            image_paths: Liste von Bildpfaden
            
        Returns:
            Dictionary mit Bildpfad als Key und Liste von Gesichtern als Value
        """
        results = {}
        
        for image_path in image_paths:
            try:
                faces = self.detect_faces(image_path=image_path)
                results[image_path] = faces
            except Exception as e:
                logger.error(f"Fehler bei Face Detection für '{image_path}': {e}")
                results[image_path] = []
        
        return results
    
    def crop_face(self, image_bytes: bytes, face_box: List[float], padding: float = 0.2) -> bytes:
        """
        Schneidet ein Gesicht aus dem Bild aus
        
        Args:
            image_bytes: Bilddaten als Bytes
            face_box: Bounding Box [x, y, width, height]
            padding: Zusätzlicher Padding-Faktor (0.2 = 20% mehr)
            
        Returns:
            Gesichts-Crop als Bytes
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            img_width, img_height = image.size
            
            x, y, w, h = face_box
            
            # Padding hinzufügen
            padding_x = int(w * padding)
            padding_y = int(h * padding)
            
            # Koordinaten berechnen (mit Clipping)
            x1 = max(0, int(x - padding_x))
            y1 = max(0, int(y - padding_y))
            x2 = min(img_width, int(x + w + padding_x))
            y2 = min(img_height, int(y + h + padding_y))
            
            # Crop
            face_crop = image.crop((x1, y1, x2, y2))
            
            # Zu Bytes konvertieren
            output = io.BytesIO()
            face_crop.save(output, format="JPEG", quality=95)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Fehler beim Croppen des Gesichts: {e}")
            raise
