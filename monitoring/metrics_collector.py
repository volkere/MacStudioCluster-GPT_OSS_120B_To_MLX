#!/usr/bin/env python3
"""
Metrics Collector für Mac Studio Cluster
Sammelt Metriken von Ray, Services und System und stellt sie für Prometheus bereit
"""

import time
import psutil
import requests
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Dict, Any
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent


class MetricsCollector:
    """Sammelt Metriken von verschiedenen Quellen"""
    
    def __init__(self):
        self.metrics = {}
        self.update_interval = 5.0  # Sekunden
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Sammelt System-Metriken"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'cpu_count': psutil.cpu_count(),
                'memory_total': memory.total,
                'memory_available': memory.available,
                'memory_used': memory.used,
                'memory_percent': memory.percent,
                'disk_total': disk.total,
                'disk_used': disk.used,
                'disk_free': disk.free,
                'disk_percent': disk.percent
            }
        except Exception as e:
            logger.error(f"Fehler beim Sammeln von System-Metriken: {e}")
            return {}
    
    def get_ray_metrics(self) -> Dict[str, Any]:
        """Sammelt Ray Cluster Metriken"""
        try:
            import ray
            if ray.is_initialized():
                cluster_resources = ray.cluster_resources()
                available_resources = ray.available_resources()
                nodes = ray.nodes()
                
                return {
                    'ray_initialized': True,
                    'nodes_count': len(nodes),
                    'cpus_total': int(cluster_resources.get('CPU', 0)),
                    'cpus_available': int(available_resources.get('CPU', 0)),
                    'gpus_total': int(cluster_resources.get('GPU', 0)),
                    'gpus_available': int(available_resources.get('GPU', 0)),
                    'memory_total': int(cluster_resources.get('memory', 0)),
                    'memory_available': int(available_resources.get('memory', 0))
                }
            else:
                return {'ray_initialized': False}
        except Exception as e:
            logger.debug(f"Ray nicht verfügbar: {e}")
            return {'ray_initialized': False}
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Sammelt Service-Status Metriken"""
        services = {
            'face_detection': {'port': 5001, 'url': 'http://localhost:5001/health'},
            'embedding': {'port': 5002, 'url': 'http://localhost:5002/health'},
            'llm': {'port': 8000, 'url': 'http://localhost:8000/v1/models'},
            'admin': {'port': 8080, 'url': 'http://localhost:8080/api/status'}
        }
        
        service_status = {}
        for name, config in services.items():
            try:
                response = requests.get(config['url'], timeout=2)
                service_status[f'{name}_status'] = 1 if response.status_code == 200 else 0
                service_status[f'{name}_response_time'] = response.elapsed.total_seconds()
            except:
                service_status[f'{name}_status'] = 0
                service_status[f'{name}_response_time'] = 0
        
        return service_status
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Sammelt alle Metriken"""
        metrics = {
            'timestamp': time.time(),
            'system': self.get_system_metrics(),
            'ray': self.get_ray_metrics(),
            'services': self.get_service_metrics()
        }
        return metrics
    
    def format_prometheus(self, metrics: Dict[str, Any]) -> str:
        """Formatiert Metriken im Prometheus-Format"""
        lines = []
        
        # System Metriken
        if 'system' in metrics:
            sys = metrics['system']
            lines.append(f"# HELP system_cpu_percent CPU usage percentage")
            lines.append(f"# TYPE system_cpu_percent gauge")
            lines.append(f"system_cpu_percent {sys.get('cpu_percent', 0)}")
            
            lines.append(f"# HELP system_memory_percent Memory usage percentage")
            lines.append(f"# TYPE system_memory_percent gauge")
            lines.append(f"system_memory_percent {sys.get('memory_percent', 0)}")
            
            lines.append(f"# HELP system_memory_used_bytes Memory used in bytes")
            lines.append(f"# TYPE system_memory_used_bytes gauge")
            lines.append(f"system_memory_used_bytes {sys.get('memory_used', 0)}")
            
            lines.append(f"# HELP system_disk_percent Disk usage percentage")
            lines.append(f"# TYPE system_disk_percent gauge")
            lines.append(f"system_disk_percent {sys.get('disk_percent', 0)}")
        
        # Ray Metriken
        if 'ray' in metrics:
            ray = metrics['ray']
            if ray.get('ray_initialized', False):
                lines.append(f"# HELP ray_nodes_count Number of Ray nodes")
                lines.append(f"# TYPE ray_nodes_count gauge")
                lines.append(f"ray_nodes_count {ray.get('nodes_count', 0)}")
                
                lines.append(f"# HELP ray_cpus_available Available CPUs in Ray cluster")
                lines.append(f"# TYPE ray_cpus_available gauge")
                lines.append(f"ray_cpus_available {ray.get('cpus_available', 0)}")
                
                lines.append(f"# HELP ray_gpus_available Available GPUs in Ray cluster")
                lines.append(f"# TYPE ray_gpus_available gauge")
                lines.append(f"ray_gpus_available {ray.get('gpus_available', 0)}")
        
        # Service Metriken
        if 'services' in metrics:
            svc = metrics['services']
            for key, value in svc.items():
                if key.endswith('_status'):
                    lines.append(f"# HELP {key} Service status (1=online, 0=offline)")
                    lines.append(f"# TYPE {key} gauge")
                    lines.append(f"{key} {value}")
                elif key.endswith('_response_time'):
                    lines.append(f"# HELP {key} Service response time in seconds")
                    lines.append(f"# TYPE {key} gauge")
                    lines.append(f"{key} {value}")
        
        return '\n'.join(lines) + '\n'
    
    def start_collection_loop(self):
        """Startet den Metriken-Sammel-Loop"""
        def loop():
            while True:
                try:
                    self.metrics = self.collect_all_metrics()
                    time.sleep(self.update_interval)
                except Exception as e:
                    logger.error(f"Fehler im Collection-Loop: {e}")
                    time.sleep(self.update_interval)
        
        thread = Thread(target=loop, daemon=True)
        thread.start()
        logger.info("Metrics Collection Loop gestartet")


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP Handler für Prometheus Metrics Endpoint"""
    
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; version=0.0.4')
            self.end_headers()
            
            collector = self.server.collector
            metrics = collector.collect_all_metrics()
            prometheus_format = collector.format_prometheus(metrics)
            self.wfile.write(prometheus_format.encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'healthy'}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Reduziere Logging
        pass


def main():
    """Hauptfunktion"""
    collector = MetricsCollector()
    collector.start_collection_loop()
    
    server = HTTPServer(('0.0.0.0', 9091), MetricsHandler)
    server.collector = collector
    
    logger.info("Metrics Collector gestartet auf http://0.0.0.0:9091/metrics")
    logger.info("Prometheus kann Metriken von http://localhost:9091/metrics abrufen")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Metrics Collector wird beendet...")
        server.shutdown()


if __name__ == '__main__':
    main()
