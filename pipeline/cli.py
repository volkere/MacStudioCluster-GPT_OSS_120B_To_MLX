#!/usr/bin/env python3
"""
CLI-Tool für Face Tagging Pipeline
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from .face_tag_pipeline import FaceTagPipeline


def process_single_image(args):
    """Verarbeitet ein einzelnes Bild"""
    pipeline = FaceTagPipeline(args.config)
    
    try:
        result = pipeline.process_photo(args.image, upload_to_minio=args.upload)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n[OK] Verarbeitung abgeschlossen")
            print(f"  Photo-ID: {result['photo_id']}")
            print(f"  Gesichter erkannt: {len(result['faces'])}")
            print(f"  Cluster erstellt: {len(result['clusters'])}")
            if result.get('errors'):
                print(f"  Fehler: {len(result['errors'])}")
                for error in result['errors']:
                    print(f"    - {error}")
    
    finally:
        pipeline.close()


def process_batch(args):
    """Verarbeitet mehrere Bilder"""
    pipeline = FaceTagPipeline(args.config)
    
    try:
        # Bildpfade aus Datei lesen oder direkt verwenden
        if args.file:
            with open(args.file, 'r') as f:
                image_paths = [line.strip() for line in f if line.strip()]
        else:
            image_paths = args.images
        
        results = pipeline.process_batch(image_paths, upload_to_minio=args.upload)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n[OK] Batch-Verarbeitung abgeschlossen")
            print(f"  Bilder verarbeitet: {len(results)}")
            total_faces = sum(len(r.get('faces', [])) for r in results)
            total_clusters = sum(len(r.get('clusters', [])) for r in results)
            print(f"  Gesamt Gesichter: {total_faces}")
            print(f"  Gesamt Cluster: {total_clusters}")
            
            errors = [r for r in results if r.get('errors')]
            if errors:
                print(f"  Bilder mit Fehlern: {len(errors)}")
    
    finally:
        pipeline.close()


def process_minio_bucket(args):
    """Verarbeitet alle Bilder in einem minIO-Bucket"""
    pipeline = FaceTagPipeline(args.config)
    
    try:
        results = pipeline.process_minio_bucket(args.bucket)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n[OK] Bucket-Verarbeitung abgeschlossen")
            print(f"  Bilder verarbeitet: {len(results)}")
            total_faces = sum(len(r.get('faces', [])) for r in results)
            total_clusters = sum(len(r.get('clusters', [])) for r in results)
            print(f"  Gesamt Gesichter: {total_faces}")
            print(f"  Gesamt Cluster: {total_clusters}")
    
    finally:
        pipeline.close()


def main():
    parser = argparse.ArgumentParser(
        description="Face Tagging Pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Einzelnes Bild verarbeiten
  python -m pipeline.cli image /path/to/image.jpg
  
  # Mehrere Bilder verarbeiten
  python -m pipeline.cli batch image1.jpg image2.jpg image3.jpg
  
  # Bilder aus Datei verarbeiten
  python -m pipeline.cli batch --file image_list.txt
  
  # Alle Bilder in minIO-Bucket verarbeiten
  python -m pipeline.cli bucket incoming
  
  # JSON-Output
  python -m pipeline.cli image image.jpg --json
        """
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Pfad zur config.yaml (Standard: pipeline/config.yaml)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output im JSON-Format"
    )
    
    parser.add_argument(
        "--upload",
        action="store_true",
        default=True,
        help="Bilder zu minIO hochladen (Standard: True)"
    )
    
    parser.add_argument(
        "--no-upload",
        dest="upload",
        action="store_false",
        help="Bilder nicht zu minIO hochladen"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Befehle")
    
    # Image-Command
    image_parser = subparsers.add_parser("image", help="Verarbeitet ein einzelnes Bild")
    image_parser.add_argument("image", type=str, help="Pfad zur Bilddatei")
    image_parser.set_defaults(func=process_single_image)
    
    # Batch-Command
    batch_parser = subparsers.add_parser("batch", help="Verarbeitet mehrere Bilder")
    batch_parser.add_argument(
        "images",
        nargs="*",
        type=str,
        help="Bildpfade (oder --file verwenden)"
    )
    batch_parser.add_argument(
        "--file",
        type=str,
        help="Datei mit Bildpfaden (eine pro Zeile)"
    )
    batch_parser.set_defaults(func=process_batch)
    
    # Bucket-Command
    bucket_parser = subparsers.add_parser("bucket", help="Verarbeitet alle Bilder in einem minIO-Bucket")
    bucket_parser.add_argument(
        "bucket",
        type=str,
        default="incoming",
        help="Bucket-Name (Standard: incoming)"
    )
    bucket_parser.set_defaults(func=process_minio_bucket)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()


