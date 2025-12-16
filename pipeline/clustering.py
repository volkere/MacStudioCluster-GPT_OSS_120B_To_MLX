"""
Clustering-Modul für Gesichts-Gruppierung (DBSCAN)
"""

import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class FaceClustering:
    """Clustering für Gesichts-Embeddings"""
    
    def __init__(self, config: dict):
        """
        Initialisiert Clustering-Modul
        
        Args:
            config: Konfiguration aus config.yaml
        """
        clustering_config = config.get("clustering", {})
        self.algorithm = clustering_config.get("algorithm", "dbscan")
        self.eps = clustering_config.get("eps", 0.5)
        self.min_samples = clustering_config.get("min_samples", 2)
        self.metric = clustering_config.get("metric", "cosine")
    
    def cluster_embeddings(self, embeddings: List[List[float]]) -> Tuple[np.ndarray, Dict[int, List[int]]]:
        """
        Gruppiert Embeddings in Cluster
        
        Args:
            embeddings: Liste von Embedding-Vektoren
            
        Returns:
            Tuple von (Labels, Cluster-Dictionary)
            - Labels: Array mit Cluster-ID für jedes Embedding (-1 = Noise)
            - Cluster-Dict: Dictionary mit Cluster-ID als Key und Liste von Indizes als Value
        """
        if not embeddings or len(embeddings) == 0:
            logger.warning("Keine Embeddings zum Clustern vorhanden")
            return np.array([]), {}
        
        # Zu numpy Array konvertieren
        X = np.array(embeddings)
        
        # DBSCAN Clustering
        if self.algorithm == "dbscan":
            if self.metric == "cosine":
                # Cosine Similarity für DBSCAN
                # DBSCAN erwartet Distanz-Matrix, daher 1 - similarity
                similarity_matrix = cosine_similarity(X)
                distance_matrix = 1 - similarity_matrix
                
                # DBSCAN mit Precomputed-Distanz
                clustering = DBSCAN(
                    eps=self.eps,
                    min_samples=self.min_samples,
                    metric="precomputed"
                )
                labels = clustering.fit_predict(distance_matrix)
            else:
                # Standard DBSCAN mit euklidischer Distanz
                clustering = DBSCAN(
                    eps=self.eps,
                    min_samples=self.min_samples,
                    metric=self.metric
                )
                labels = clustering.fit_predict(X)
        else:
            raise ValueError(f"Unbekannter Clustering-Algorithmus: {self.algorithm}")
        
        # Cluster-Dictionary erstellen
        cluster_dict = {}
        for idx, label in enumerate(labels):
            if label not in cluster_dict:
                cluster_dict[label] = []
            cluster_dict[label].append(idx)
        
        n_clusters = len([k for k in cluster_dict.keys() if k != -1])
        n_noise = len(cluster_dict.get(-1, []))
        
        logger.info(f"Clustering abgeschlossen: {n_clusters} Cluster, {n_noise} Noise-Punkte")
        
        return labels, cluster_dict
    
    def get_cluster_statistics(self, labels: np.ndarray, cluster_dict: Dict[int, List[int]]) -> Dict[str, Any]:
        """
        Berechnet Statistiken über die Cluster
        
        Args:
            labels: Cluster-Labels
            cluster_dict: Cluster-Dictionary
            
        Returns:
            Dictionary mit Statistiken
        """
        n_clusters = len([k for k in cluster_dict.keys() if k != -1])
        n_noise = len(cluster_dict.get(-1, []))
        cluster_sizes = [len(indices) for label, indices in cluster_dict.items() if label != -1]
        
        stats = {
            "n_clusters": n_clusters,
            "n_noise": n_noise,
            "n_total": len(labels),
            "cluster_sizes": cluster_sizes,
            "avg_cluster_size": np.mean(cluster_sizes) if cluster_sizes else 0,
            "max_cluster_size": max(cluster_sizes) if cluster_sizes else 0,
            "min_cluster_size": min(cluster_sizes) if cluster_sizes else 0
        }
        
        return stats
    
    def get_cluster_representative(self, cluster_indices: List[int], embeddings: List[List[float]]) -> int:
        """
        Findet repräsentatives Embedding für einen Cluster (z.B. Zentroid)
        
        Args:
            cluster_indices: Indizes der Embeddings im Cluster
            embeddings: Liste aller Embeddings
            
        Returns:
            Index des repräsentativen Embeddings
        """
        if not cluster_indices:
            return -1
        
        cluster_embeddings = np.array([embeddings[i] for i in cluster_indices])
        
        # Zentroid berechnen
        centroid = np.mean(cluster_embeddings, axis=0)
        
        # Nächstes Embedding zum Zentroid finden
        distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
        representative_idx = cluster_indices[np.argmin(distances)]
        
        return representative_idx


