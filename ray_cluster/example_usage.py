#!/usr/bin/env python3
"""
Beispiel-Verwendung der Ray-basierten Pipeline
"""

from ray_cluster.ray_pipeline import RayFaceTagPipeline
import json

def main():
    # Option 1: Lokaler Ray Cluster (für Testing)
    print("=== Lokaler Ray Cluster ===")
    pipeline = RayFaceTagPipeline()
    
    try:
        # Cluster-Status
        status = pipeline.get_cluster_status()
        print(f"Nodes: {status['nodes']}")
        print(f"Resources: {json.dumps(status['cluster_resources'], indent=2)}")
        
        # Beispiel-Verarbeitung
        # result = pipeline.process_photo_distributed("/path/to/image.jpg")
        # print(f"Verarbeitet: {result['photo_id']}")
        # print(f"Gesichter: {len(result['faces'])}")
        
    finally:
        pipeline.shutdown()
    
    # Option 2: Verbindung zu Remote Ray Cluster
    print("\n=== Remote Ray Cluster ===")
    # pipeline = RayFaceTagPipeline(ray_address="ray://10.10.10.12:10001")
    
    # try:
    #     status = pipeline.get_cluster_status()
    #     print(f"Nodes: {status['nodes']}")
    #     
    #     # Batch-Verarbeitung über mehrere Nodes
    #     results = pipeline.process_batch_distributed([
    #         "/path/to/image1.jpg",
    #         "/path/to/image2.jpg",
    #         "/path/to/image3.jpg"
    #     ])
    #     print(f"Verarbeitet: {len(results)} Bilder")
    #     
    # finally:
    #     pipeline.shutdown()

if __name__ == "__main__":
    main()


