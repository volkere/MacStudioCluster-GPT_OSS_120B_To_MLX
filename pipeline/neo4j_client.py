"""
Neo4j Client für Graph-Datenbank-Integration
"""

import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
import json

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Client für Neo4j Graph-Datenbank"""
    
    def __init__(self, config: dict):
        """
        Initialisiert Neo4j Client
        
        Args:
            config: Konfiguration aus config.yaml
        """
        neo4j_config = config.get("neo4j", {})
        self.driver = GraphDatabase.driver(
            neo4j_config["uri"],
            auth=(neo4j_config["user"], neo4j_config["password"])
        )
        self.database = neo4j_config.get("database", "neo4j")
        self._verify_connection()
    
    def _verify_connection(self):
        """Verifiziert die Verbindung zur Neo4j-Datenbank"""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 as test")
                result.single()
            logger.info("Neo4j-Verbindung erfolgreich")
        except Exception as e:
            logger.error(f"Fehler bei Neo4j-Verbindung: {e}")
            raise
    
    def execute_cypher(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Führt einen Cypher-Query aus
        
        Args:
            query: Cypher-Query
            parameters: Optional Parameter für den Query
            
        Returns:
            Liste von Ergebnissen
        """
        if parameters is None:
            parameters = {}
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters)
                records = [dict(record) for record in result]
                logger.debug(f"Cypher-Query ausgeführt: {len(records)} Ergebnisse")
                return records
        except Exception as e:
            logger.error(f"Fehler beim Ausführen von Cypher-Query: {e}")
            logger.error(f"Query: {query}")
            raise
    
    def create_person(self, name: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Erstellt einen Person-Node
        
        Args:
            name: Name der Person
            properties: Zusätzliche Properties
            
        Returns:
            Erstellter Node
        """
        if properties is None:
            properties = {}
        
        properties["name"] = name
        
        query = """
        MERGE (p:Person {name: $name})
        SET p += $properties
        RETURN p
        """
        
        result = self.execute_cypher(query, {
            "name": name,
            "properties": properties
        })
        
        if result:
            logger.info(f"Person '{name}' erstellt/aktualisiert")
            return result[0]
        return {}
    
    def create_event(self, event_type: str, date: Optional[str] = None, 
                    location: Optional[str] = None, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Erstellt einen Event-Node
        
        Args:
            event_type: Typ des Events
            date: Datum (optional)
            location: Ort (optional)
            properties: Zusätzliche Properties
            
        Returns:
            Erstellter Node
        """
        if properties is None:
            properties = {}
        
        properties["type"] = event_type
        if date:
            properties["date"] = date
        if location:
            properties["location"] = location
        
        query = """
        CREATE (e:Event)
        SET e = $properties
        RETURN e
        """
        
        result = self.execute_cypher(query, {"properties": properties})
        
        if result:
            logger.info(f"Event '{event_type}' erstellt")
            return result[0]
        return {}
    
    def create_photo(self, photo_id: str, minio_path: str, 
                    properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Erstellt einen Photo-Node
        
        Args:
            photo_id: Eindeutige Photo-ID
            minio_path: Pfad in minIO
            properties: Zusätzliche Properties
            
        Returns:
            Erstellter Node
        """
        if properties is None:
            properties = {}
        
        properties["id"] = photo_id
        properties["minio_path"] = minio_path
        
        query = """
        MERGE (ph:Photo {id: $photo_id})
        SET ph += $properties
        RETURN ph
        """
        
        result = self.execute_cypher(query, {
            "photo_id": photo_id,
            "properties": properties
        })
        
        if result:
            logger.info(f"Photo '{photo_id}' erstellt/aktualisiert")
            return result[0]
        return {}
    
    def link_person_to_event(self, person_name: str, event_id: str, relationship_type: str = "ATTENDED"):
        """
        Verknüpft Person mit Event
        
        Args:
            person_name: Name der Person
            event_id: ID des Events
            relationship_type: Typ der Beziehung
        """
        query = """
        MATCH (p:Person {name: $person_name})
        MATCH (e:Event)
        WHERE id(e) = $event_id
        MERGE (p)-[r:ATTENDED]->(e)
        RETURN r
        """
        
        result = self.execute_cypher(query, {
            "person_name": person_name,
            "event_id": event_id
        })
        
        if result:
            logger.debug(f"Person '{person_name}' mit Event verknüpft")
    
    def link_person_to_photo(self, person_name: str, photo_id: str, relationship_type: str = "APPEARS_IN"):
        """
        Verknüpft Person mit Photo
        
        Args:
            person_name: Name der Person
            photo_id: ID des Photos
            relationship_type: Typ der Beziehung
        """
        query = """
        MATCH (p:Person {name: $person_name})
        MATCH (ph:Photo {id: $photo_id})
        MERGE (p)-[r:APPEARS_IN]->(ph)
        RETURN r
        """
        
        result = self.execute_cypher(query, {
            "person_name": person_name,
            "photo_id": photo_id
        })
        
        if result:
            logger.debug(f"Person '{person_name}' mit Photo '{photo_id}' verknüpft")
    
    def execute_custom_cypher(self, cypher_query: str) -> List[Dict[str, Any]]:
        """
        Führt einen benutzerdefinierten Cypher-Query aus (z.B. von LLM generiert)
        
        Args:
            cypher_query: Cypher-Query-String
            
        Returns:
            Liste von Ergebnissen
        """
        # Sicherheitsprüfung: Nur SELECT-ähnliche Queries erlauben
        query_upper = cypher_query.strip().upper()
        dangerous_keywords = ["DROP", "DELETE", "DETACH DELETE", "REMOVE"]
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                logger.warning(f"Gefährlicher Query erkannt, wird nicht ausgeführt: {keyword}")
                return []
        
        return self.execute_cypher(cypher_query)
    
    def close(self):
        """Schließt die Verbindung zur Neo4j-Datenbank"""
        self.driver.close()
        logger.info("Neo4j-Verbindung geschlossen")


