"""
minIO Client für Objektspeicher-Integration
"""

import io
import logging
from typing import Optional, List, BinaryIO
from pathlib import Path
from minio import Minio
from minio.error import S3Error
import yaml

logger = logging.getLogger(__name__)


class MinIOClient:
    """Client für minIO Objektspeicher"""
    
    def __init__(self, config: dict):
        """
        Initialisiert minIO Client
        
        Args:
            config: Konfiguration aus config.yaml
        """
        minio_config = config.get("minio", {})
        self.client = Minio(
            minio_config["endpoint"],
            access_key=minio_config["access_key"],
            secret_key=minio_config["secret_key"],
            secure=minio_config.get("secure", False)
        )
        self.buckets = minio_config.get("buckets", {})
        self._ensure_buckets()
    
    def _ensure_buckets(self):
        """Stellt sicher, dass alle benötigten Buckets existieren"""
        for bucket_name in self.buckets.values():
            try:
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name)
                    logger.info(f"Bucket '{bucket_name}' erstellt")
            except S3Error as e:
                logger.error(f"Fehler beim Erstellen von Bucket '{bucket_name}': {e}")
    
    def upload_image(self, image_path: str, bucket: str, object_name: Optional[str] = None) -> str:
        """
        Lädt ein Bild zu minIO hoch
        
        Args:
            image_path: Pfad zur Bilddatei
            bucket: Bucket-Name (z.B. 'incoming' oder 'processed')
            object_name: Optionaler Objektname (Standard: Dateiname)
            
        Returns:
            Objektname im Bucket
        """
        if object_name is None:
            object_name = Path(image_path).name
        
        bucket_name = self.buckets.get(bucket, bucket)
        
        try:
            self.client.fput_object(
                bucket_name,
                object_name,
                image_path
            )
            logger.info(f"Bild '{image_path}' zu '{bucket_name}/{object_name}' hochgeladen")
            return object_name
        except S3Error as e:
            logger.error(f"Fehler beim Hochladen von '{image_path}': {e}")
            raise
    
    def upload_bytes(self, data: bytes, bucket: str, object_name: str, content_type: str = "image/jpeg") -> str:
        """
        Lädt Bytes zu minIO hoch
        
        Args:
            data: Bilddaten als Bytes
            bucket: Bucket-Name
            object_name: Objektname
            content_type: MIME-Type
            
        Returns:
            Objektname im Bucket
        """
        bucket_name = self.buckets.get(bucket, bucket)
        
        try:
            data_stream = io.BytesIO(data)
            self.client.put_object(
                bucket_name,
                object_name,
                data_stream,
                length=len(data),
                content_type=content_type
            )
            logger.info(f"Daten zu '{bucket_name}/{object_name}' hochgeladen")
            return object_name
        except S3Error as e:
            logger.error(f"Fehler beim Hochladen von Bytes: {e}")
            raise
    
    def download_image(self, bucket: str, object_name: str, file_path: str):
        """
        Lädt ein Bild von minIO herunter
        
        Args:
            bucket: Bucket-Name
            object_name: Objektname
            file_path: Zielpfad
        """
        bucket_name = self.buckets.get(bucket, bucket)
        
        try:
            self.client.fget_object(bucket_name, object_name, file_path)
            logger.info(f"Bild '{object_name}' von '{bucket_name}' heruntergeladen")
        except S3Error as e:
            logger.error(f"Fehler beim Herunterladen von '{object_name}': {e}")
            raise
    
    def get_image_bytes(self, bucket: str, object_name: str) -> bytes:
        """
        Lädt Bilddaten als Bytes von minIO
        
        Args:
            bucket: Bucket-Name
            object_name: Objektname
            
        Returns:
            Bilddaten als Bytes
        """
        bucket_name = self.buckets.get(bucket, bucket)
        
        try:
            response = self.client.get_object(bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            logger.debug(f"Bild '{object_name}' von '{bucket_name}' geladen ({len(data)} bytes)")
            return data
        except S3Error as e:
            logger.error(f"Fehler beim Laden von '{object_name}': {e}")
            raise
    
    def list_images(self, bucket: str, prefix: str = "") -> List[str]:
        """
        Listet alle Bilder in einem Bucket
        
        Args:
            bucket: Bucket-Name
            prefix: Optionaler Prefix-Filter
            
        Returns:
            Liste von Objektnamen
        """
        bucket_name = self.buckets.get(bucket, bucket)
        images = []
        
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            for obj in objects:
                if obj.object_name.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
                    images.append(obj.object_name)
            return images
        except S3Error as e:
            logger.error(f"Fehler beim Auflisten von '{bucket_name}': {e}")
            return []


