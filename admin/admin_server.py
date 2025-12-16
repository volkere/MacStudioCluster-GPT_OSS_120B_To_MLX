#!/usr/bin/env python3
"""
Admin Server für Mac Studio Cluster
Web-Interface für Installation, Konfiguration und Verwaltung
"""

import os
import sys
import subprocess
import json
import yaml
import logging
from pathlib import Path
from flask import Flask, render_template, jsonify, request, Response, stream_with_context
from flask_cors import CORS
import psutil
import requests

# Pfade
PROJECT_ROOT = Path(__file__).parent.parent
SERVICES_DIR = PROJECT_ROOT / "services"
RAY_CLUSTER_DIR = PROJECT_ROOT / "ray_cluster"
NETWORK_DIR = PROJECT_ROOT / "network"
PIPELINE_DIR = PROJECT_ROOT / "pipeline"
MLX_ENV = PROJECT_ROOT / "mlx_env"
NODE_CONFIG_FILE = PROJECT_ROOT / ".node_config.json"

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_command(command, cwd=None, shell=False):
    """Führt einen Befehl aus und gibt Output zurück"""
    try:
        if isinstance(command, str) and not shell:
            command = command.split()
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=cwd,
            shell=shell
        )
        
        for line in iter(process.stdout.readline, ''):
            yield line
        
        process.wait()
    except Exception as e:
        yield f"Fehler: {str(e)}\n"


@app.route('/')
def index():
    """Hauptseite"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Gibt Cluster-Status zurück"""
    try:
        # Cluster Status (Ray)
        cluster_status = {
            'nodes': 0,
            'cpus': 0,
            'gpus': 0
        }
        
        try:
            import ray
            if ray.is_initialized():
                cluster_resources = ray.cluster_resources()
                cluster_status = {
                    'nodes': len(ray.nodes()),
                    'cpus': int(cluster_resources.get('CPU', 0)),
                    'gpus': int(cluster_resources.get('GPU', 0))
                }
        except:
            pass
        
        # Services Status
        services_status = {}
        service_ports = {
            'face_detection': 5001,
            'embedding': 5002,
            'llm': 8000,
            'minio': 9000,
            'neo4j': 7687
        }
        
        for service, port in service_ports.items():
            try:
                if service == 'llm':
                    response = requests.get(f"http://localhost:{port}/v1/models", timeout=2)
                else:
                    response = requests.get(f"http://localhost:{port}/health", timeout=2)
                services_status[service] = response.status_code == 200
            except:
                services_status[service] = False
        
        # System Status
        system_status = {
            'ram': psutil.virtual_memory().total,
            'disk': psutil.disk_usage('/').total
        }
        
        return jsonify({
            'cluster': cluster_status,
            'services': services_status,
            'system': system_status
        })
    except Exception as e:
        logger.error(f"Fehler beim Laden des Status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/install', methods=['POST'])
def install():
    """Startet Installation"""
    def generate():
        yield "=== Installation startet ===\n"
        
        # 1. Virtual Environment erstellen
        yield "Schritt 1: Erstelle Virtual Environment...\n"
        if not MLX_ENV.exists():
            for line in run_command(['python3', '-m', 'venv', str(MLX_ENV)], cwd=PROJECT_ROOT):
                yield line
        else:
            yield "Virtual Environment existiert bereits\n"
        
        # 2. Dependencies installieren
        yield "\nSchritt 2: Installiere Dependencies...\n"
        pip_cmd = [str(MLX_ENV / 'bin' / 'pip'), 'install', '-e', '.']
        for line in run_command(pip_cmd, cwd=PROJECT_ROOT):
            yield line
        
        # 3. exo Setup (optional)
        yield "\nSchritt 3: Setup exo Framework...\n"
        exo_dir = PROJECT_ROOT / 'exo'
        if exo_dir.exists():
            exo_venv = exo_dir / '.venv'
            if not exo_venv.exists():
                for line in run_command(['python3', '-m', 'venv', '.venv'], cwd=exo_dir):
                    yield line
            pip_exo = [str(exo_venv / 'bin' / 'pip'), 'install', '-e', '.']
            for line in run_command(pip_exo, cwd=exo_dir):
                yield line
        
        yield "\n=== Installation abgeschlossen ===\n"
    
    return Response(stream_with_context(generate()), mimetype='text/plain')


@app.route('/api/services/<service>/start', methods=['POST'])
def start_service(service):
    """Startet einen Service"""
    try:
        service_scripts = {
            'face_detection': SERVICES_DIR / 'face_detection_service.py',
            'embedding': SERVICES_DIR / 'embedding_service.py',
            'llm': None  # Wird über exo gestartet
        }
        
        if service == 'llm':
            # exo starten
            exo_dir = PROJECT_ROOT / 'exo'
            cmd = [str(exo_dir / '.venv' / 'bin' / 'exo'), '--chatgpt-api-port', '8000', '--disable-tui']
            subprocess.Popen(cmd, cwd=exo_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif service in service_scripts:
            script = service_scripts[service]
            if script and script.exists():
                cmd = [str(MLX_ENV / 'bin' / 'python'), str(script)]
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                return jsonify({'success': False, 'error': 'Service-Script nicht gefunden'}), 404
        else:
            return jsonify({'success': False, 'error': 'Unbekannter Service'}), 404
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Fehler beim Starten von {service}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/services/<service>/stop', methods=['POST'])
def stop_service(service):
    """Stoppt einen Service"""
    try:
        service_ports = {
            'face_detection': 5001,
            'embedding': 5002,
            'llm': 8000
        }
        
        if service in service_ports:
            port = service_ports[service]
            # Finde Prozess auf Port
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            proc.kill()
                            return jsonify({'success': True})
                except:
                    pass
            
            return jsonify({'success': False, 'error': 'Service nicht gefunden'})
        else:
            return jsonify({'success': False, 'error': 'Unbekannter Service'}), 404
    except Exception as e:
        logger.error(f"Fehler beim Stoppen von {service}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/services/status')
def services_status():
    """Gibt Status aller Services zurück"""
    service_ports = {
        'face_detection': 5001,
        'embedding': 5002,
        'llm': 8000,
        'minio': 9000,
        'neo4j': 7687
    }
    
    status = {}
    for service, port in service_ports.items():
        try:
            if service == 'llm':
                response = requests.get(f"http://localhost:{port}/v1/models", timeout=2)
            else:
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
            status[service] = response.status_code == 200
        except:
            status[service] = False
    
    return jsonify(status)


@app.route('/api/vlan/setup', methods=['POST'])
def vlan_setup():
    """Startet VLAN Setup"""
    data = request.json
    node_type = data.get('node_type')
    management_ip = data.get('management_ip')
    worker_ip = data.get('worker_ip')
    storage_ip = data.get('storage_ip')
    
    def generate():
        yield f"=== VLAN Setup für {node_type} ===\n"
        
        # Baue Command
        cmd = ['sudo', str(NETWORK_DIR / 'setup_vlan.sh'), node_type]
        if management_ip:
            cmd.append(management_ip)
        if worker_ip:
            cmd.append(worker_ip)
        if storage_ip:
            cmd.append(storage_ip)
        
        yield f"Führe aus: {' '.join(cmd)}\n"
        yield "Hinweis: Benötigt Root-Rechte (sudo)\n"
        
        # Führe aus (ohne sudo für Demo, in Produktion würde man sudo verwenden)
        for line in run_command(cmd, cwd=NETWORK_DIR, shell=False):
            yield line
        
        yield "\n=== VLAN Setup abgeschlossen ===\n"
    
    return Response(stream_with_context(generate()), mimetype='text/plain')


@app.route('/api/config/<config_type>', methods=['GET'])
def get_config(config_type):
    """Lädt Konfiguration"""
    try:
        if config_type == 'pipeline':
            config_path = PIPELINE_DIR / 'config.yaml'
        elif config_type == 'ray':
            config_path = RAY_CLUSTER_DIR / 'config.yaml'
        elif config_type == 'vlan':
            config_path = NETWORK_DIR / 'vlan_config.yaml'
        else:
            return jsonify({'error': 'Unbekannter Konfigurationstyp'}), 404
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return jsonify(config)
        else:
            return jsonify({'error': 'Konfigurationsdatei nicht gefunden'}), 404
    except Exception as e:
        logger.error(f"Fehler beim Laden der Konfiguration: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/config/<config_type>', methods=['POST'])
def save_config(config_type):
    """Speichert Konfiguration"""
    try:
        if config_type == 'pipeline':
            config_path = PIPELINE_DIR / 'config.yaml'
        elif config_type == 'ray':
            config_path = RAY_CLUSTER_DIR / 'config.yaml'
        elif config_type == 'vlan':
            config_path = NETWORK_DIR / 'vlan_config.yaml'
        else:
            return jsonify({'success': False, 'error': 'Unbekannter Konfigurationstyp'}), 404
        
        config = request.json
        
        # Merge mit existierender Konfiguration
        if config_path.exists():
            with open(config_path, 'r') as f:
                existing_config = yaml.safe_load(f) or {}
            # Deep merge
            def deep_merge(base, update):
                for key, value in update.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        deep_merge(base[key], value)
                    else:
                        base[key] = value
                return base
            config = deep_merge(existing_config, config)
        
        # Speichere
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/node/type', methods=['GET'])
def get_node_type():
    """Lädt den konfigurierten Node-Typ"""
    try:
        if NODE_CONFIG_FILE.exists():
            with open(NODE_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return jsonify({'node_type': config.get('node_type', 'management')})
        return jsonify({'node_type': 'management'})  # Default
    except Exception as e:
        logger.error(f"Fehler beim Laden des Node-Typs: {e}")
        return jsonify({'node_type': 'management'}), 200


@app.route('/api/node/type', methods=['POST'])
def set_node_type():
    """Setzt den Node-Typ"""
    try:
        data = request.json
        node_type = data.get('node_type')
        
        if node_type not in ['management', 'worker', 'storage']:
            return jsonify({'success': False, 'error': 'Ungültiger Node-Typ'}), 400
        
        config = {'node_type': node_type}
        with open(NODE_CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        
        return jsonify({'success': True, 'node_type': node_type})
    except Exception as e:
        logger.error(f"Fehler beim Setzen des Node-Typs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/services/start-all', methods=['POST'])
def start_all_services():
    """Startet alle Services basierend auf Node-Typ"""
    try:
        # Lade Node-Typ
        node_type = 'management'
        if NODE_CONFIG_FILE.exists():
            with open(NODE_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                node_type = config.get('node_type', 'management')
        
        def generate():
            yield f"=== Starte Services für {node_type} Node ===\n\n"
            
            # Services basierend auf Node-Typ
            services_to_start = []
            if node_type == 'management':
                services_to_start = ['llm']  # Management: LLM (exo)
            elif node_type == 'worker':
                services_to_start = ['face_detection', 'embedding']  # Worker: Face Detection + Embedding
            elif node_type == 'storage':
                services_to_start = []  # Storage: minIO wird separat gestartet
                yield "Hinweis: minIO sollte manuell gestartet werden\n"
            
            # Starte Services über start_services.sh
            if services_to_start:
                script_path = SERVICES_DIR / 'start_services.sh'
                if script_path.exists():
                    yield f"Starte Services: {', '.join(services_to_start)}\n"
                    for line in run_command(['bash', str(script_path)], cwd=SERVICES_DIR, shell=False):
                        yield line
                else:
                    yield f"Warnung: start_services.sh nicht gefunden\n"
            
            # Ray Cluster starten (nur für Management und Worker)
            if node_type in ['management', 'worker']:
                yield "\n=== Starte Ray Cluster ===\n"
                ray_script = RAY_CLUSTER_DIR / 'start_ray_cluster.sh'
                if ray_script.exists():
                    ray_mode = 'head' if node_type == 'management' else 'worker'
                    yield f"Starte Ray als {ray_mode} node\n"
                    
                    if ray_mode == 'worker':
                        # Lade Head-Adresse aus Config
                        ray_config_path = RAY_CLUSTER_DIR / 'config.yaml'
                        head_address = None
                        if ray_config_path.exists():
                            try:
                                with open(ray_config_path, 'r') as f:
                                    ray_config = yaml.safe_load(f)
                                    head_node = ray_config.get('head_node', {})
                                    head_address = f"{head_node.get('ip', 'localhost')}:{head_node.get('gcs_port', 6380)}"
                            except:
                                pass
                        
                        if head_address:
                            for line in run_command(['bash', str(ray_script), ray_mode, head_address], cwd=RAY_CLUSTER_DIR, shell=False):
                                yield line
                        else:
                            yield "Warnung: Head-Adresse nicht in Config gefunden. Worker benötigt Head-Adresse.\n"
                    else:
                        for line in run_command(['bash', str(ray_script), ray_mode], cwd=RAY_CLUSTER_DIR, shell=False):
                            yield line
                else:
                    yield "Warnung: start_ray_cluster.sh nicht gefunden\n"
            
            yield "\n=== Services gestartet ===\n"
        
        return Response(stream_with_context(generate()), mimetype='text/plain')
    except Exception as e:
        logger.error(f"Fehler beim Starten der Services: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/services/stop-all', methods=['POST'])
def stop_all_services():
    """Stoppt alle Services"""
    try:
        def generate():
            yield "=== Stoppe alle Services ===\n\n"
            
            # Stoppe Services
            stop_script = SERVICES_DIR / 'stop_services.sh'
            if stop_script.exists():
                yield "Stoppe Python-Services...\n"
                for line in run_command(['bash', str(stop_script)], cwd=SERVICES_DIR, shell=False):
                    yield line
            
            # Stoppe Ray Cluster
            ray_stop_script = RAY_CLUSTER_DIR / 'stop_ray_cluster.sh'
            if ray_stop_script.exists():
                yield "\nStoppe Ray Cluster...\n"
                for line in run_command(['bash', str(ray_stop_script)], cwd=RAY_CLUSTER_DIR, shell=False):
                    yield line
            
            yield "\n=== Alle Services gestoppt ===\n"
        
        return Response(stream_with_context(generate()), mimetype='text/plain')
    except Exception as e:
        logger.error(f"Fehler beim Stoppen der Services: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


MONITORING_DIR = PROJECT_ROOT / "monitoring"

@app.route('/api/monitoring/status')
def monitoring_status():
    """Gibt Status der Monitoring-Services zurück"""
    try:
        status = {
            'grafana': False,
            'prometheus': False,
            'metrics_collector': False
        }
        
        # Prüfe Grafana
        try:
            response = requests.get('http://localhost:3000/api/health', timeout=2)
            status['grafana'] = response.status_code == 200
        except:
            pass
        
        # Prüfe Prometheus
        try:
            response = requests.get('http://localhost:9090/-/healthy', timeout=2)
            status['prometheus'] = response.status_code == 200
        except:
            pass
        
        # Prüfe Metrics Collector
        try:
            response = requests.get('http://localhost:9091/health', timeout=2)
            status['metrics_collector'] = response.status_code == 200
        except:
            pass
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"Fehler beim Laden des Monitoring-Status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/<service>/start', methods=['POST'])
def start_monitoring_service(service):
    """Startet einen Monitoring-Service"""
    try:
        scripts = {
            'grafana': MONITORING_DIR / 'start_grafana.sh',
            'prometheus': MONITORING_DIR / 'start_prometheus.sh',
            'metrics_collector': MONITORING_DIR / 'start_metrics_collector.sh'
        }
        
        if service not in scripts:
            return jsonify({'success': False, 'error': 'Unbekannter Service'}), 404
        
        script = scripts[service]
        if not script.exists():
            return jsonify({'success': False, 'error': 'Script nicht gefunden'}), 404
        
        subprocess.Popen(['bash', str(script)], cwd=MONITORING_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Fehler beim Starten von {service}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/monitoring/<service>/stop', methods=['POST'])
def stop_monitoring_service(service):
    """Stoppt einen Monitoring-Service"""
    try:
        ports = {
            'grafana': 3000,
            'prometheus': 9090,
            'metrics_collector': 9091
        }
        
        if service not in ports:
            return jsonify({'success': False, 'error': 'Unbekannter Service'}), 404
        
        port = ports[service]
        pids = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        pids.append(proc.pid)
            except:
                pass
        
        if pids:
            for pid in pids:
                try:
                    proc = psutil.Process(pid)
                    proc.terminate()
                except:
                    pass
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Service nicht gefunden'})
    except Exception as e:
        logger.error(f"Fehler beim Stoppen von {service}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)


