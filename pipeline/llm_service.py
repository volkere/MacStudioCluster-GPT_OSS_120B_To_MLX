"""
LLM Service Integration (GPT-OSS-120B / MLX-LM)
"""

import logging
import requests
import time
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class LLMService:
    """Client für LLM Service (MLX-optimiert)"""
    
    def __init__(self, config: dict):
        """
        Initialisiert LLM Service Client
        
        Args:
            config: Konfiguration aus config.yaml
        """
        service_config = config.get("services", {}).get("llm", {})
        self.url = service_config.get("url", "http://localhost:8000")
        self.timeout = service_config.get("timeout", 120)
        self.retry_attempts = service_config.get("retry_attempts", 2)
        self.model = service_config.get("model", "gpt-oss-120b-4bit")
    
    def _create_prompt(self, prompt_type: str, context: Dict[str, Any]) -> str:
        """
        Erstellt Prompt basierend auf Typ und Kontext
        
        Args:
            prompt_type: Typ des Prompts ('cluster_naming', 'event_enrichment', 'cypher_generation')
            context: Kontext-Informationen
            
        Returns:
            Formatierter Prompt
        """
        if prompt_type == "cluster_naming":
            n_faces = context.get("n_faces", 0)
            return f"""Du siehst {n_faces} Gesichter, die wahrscheinlich zur gleichen Person gehören.
Bitte gib einen passenden Namen für diese Person an. Berücksichtige:
- Geschlecht und geschätztes Alter
- Auffällige Merkmale
- Falls möglich, historischen Kontext

Antworte nur mit dem Namen, maximal 3 Wörter."""
        
        elif prompt_type == "event_enrichment":
            cluster_name = context.get("cluster_name", "Person")
            image_info = context.get("image_info", {})
            return f"""Analysiere das Bild mit {cluster_name} und gib an:
1. Geschätztes Datum (Jahr, ggf. Jahrzehnt)
2. Event-Typ (z.B. Geburtstag, Hochzeit, Urlaub)
3. Ort (falls erkennbar)
4. Weitere Personen (Anzahl, Beziehungen)

Bild-Info: {json.dumps(image_info, indent=2)}

Antworte im JSON-Format:
{{
  "date": "Jahr oder Jahrzehnt",
  "event_type": "Event-Typ",
  "location": "Ort oder null",
  "other_people": "Beschreibung"
}}"""
        
        elif prompt_type == "cypher_generation":
            cluster_name = context.get("cluster_name", "Person")
            event_info = context.get("event_info", {})
            return f"""Generiere einen Neo4j Cypher-Query, um folgende Informationen zu speichern:

Person: {cluster_name}
Event: {json.dumps(event_info, indent=2)}

Erstelle Nodes für:
- Person (mit Name)
- Event (mit Datum, Typ, Ort)
- Photo (mit Metadaten)
- Beziehungen zwischen diesen Nodes

Antworte nur mit dem Cypher-Query, keine Erklärungen."""
        
        else:
            raise ValueError(f"Unbekannter Prompt-Typ: {prompt_type}")
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Generiert Text mit LLM
        
        Args:
            prompt: Eingabe-Prompt
            max_tokens: Maximale Anzahl von Tokens
            temperature: Temperature für Sampling
            
        Returns:
            Generierter Text
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    f"{self.url}/v1/chat/completions",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                logger.debug(f"LLM-Response generiert ({len(content)} Zeichen)")
                return content.strip()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Versuch {attempt + 1}/{self.retry_attempts} fehlgeschlagen: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"LLM-Generierung nach {self.retry_attempts} Versuchen fehlgeschlagen")
                    raise
    
    def ask_for_cluster_name(self, n_faces: int) -> str:
        """
        Fragt LLM nach einem Namen für einen Cluster
        
        Args:
            n_faces: Anzahl der Gesichter im Cluster
            
        Returns:
            Vorgeschlagener Name
        """
        context = {"n_faces": n_faces}
        prompt = self._create_prompt("cluster_naming", context)
        return self.generate(prompt, max_tokens=50, temperature=0.8)
    
    def enrich_event_info(self, cluster_name: str, image_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reichert Event-Informationen mit LLM an
        
        Args:
            cluster_name: Name des Clusters/Person
            image_info: Bild-Metadaten
            
        Returns:
            Dictionary mit Event-Informationen
        """
        context = {
            "cluster_name": cluster_name,
            "image_info": image_info
        }
        prompt = self._create_prompt("event_enrichment", context)
        response = self.generate(prompt, max_tokens=200, temperature=0.7)
        
        try:
            # JSON aus Response extrahieren
            import re
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                logger.warning("Konnte JSON aus LLM-Response nicht extrahieren")
                return {"date": None, "event_type": None, "location": None}
        except json.JSONDecodeError as e:
            logger.error(f"Fehler beim Parsen der LLM-Response: {e}")
            return {"date": None, "event_type": None, "location": None}
    
    def generate_cypher_query(self, cluster_name: str, event_info: Dict[str, Any]) -> str:
        """
        Generiert Neo4j Cypher-Query mit LLM
        
        Args:
            cluster_name: Name des Clusters/Person
            event_info: Event-Informationen
            
        Returns:
            Cypher-Query als String
        """
        context = {
            "cluster_name": cluster_name,
            "event_info": event_info
        }
        prompt = self._create_prompt("cypher_generation", context)
        return self.generate(prompt, max_tokens=300, temperature=0.5)
