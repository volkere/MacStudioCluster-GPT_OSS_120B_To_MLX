#!/usr/bin/env python3
"""
Beispiel-Script für die Verwendung der Face Tagging Pipeline
"""

from pipeline.face_tag_pipeline import FaceTagPipeline
import json

def main():
    # Pipeline initialisieren
    print("Initialisiere Pipeline...")
    pipeline = FaceTagPipeline()
    
    try:
        # Beispiel 1: Einzelnes Bild verarbeiten
        print("\n=== Beispiel 1: Einzelnes Bild ===")
        result = pipeline.process_photo(
            "/path/to/your/image.jpg",
            upload_to_minio=True
        )
        
        print(f"Photo-ID: {result['photo_id']}")
        print(f"Gesichter erkannt: {len(result['faces'])}")
        print(f"Cluster erstellt: {len(result['clusters'])}")
        
        # Beispiel 2: Batch-Verarbeitung
        print("\n=== Beispiel 2: Batch-Verarbeitung ===")
        image_paths = [
            "/path/to/image1.jpg",
            "/path/to/image2.jpg",
            "/path/to/image3.jpg"
        ]
        
        results = pipeline.process_batch(image_paths, upload_to_minio=True)
        print(f"Bilder verarbeitet: {len(results)}")
        
        # Beispiel 3: minIO-Bucket verarbeiten
        print("\n=== Beispiel 3: minIO-Bucket ===")
        # results = pipeline.process_minio_bucket("incoming")
        # print(f"Bilder verarbeitet: {len(results)}")
        
        # Beispiel 4: JSON-Output speichern
        print("\n=== Beispiel 4: JSON-Output ===")
        with open("pipeline_result.json", "w") as f:
            json.dump(result, f, indent=2)
        print("Ergebnis gespeichert in pipeline_result.json")
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Verbindungen schließen
        pipeline.close()
        print("\nPipeline geschlossen")

if __name__ == "__main__":
    main()


