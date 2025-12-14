// Admin Dashboard JavaScript

const API_BASE = '/api';

// Status-Updates
let statusInterval = null;

// Initialisierung
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadStatus();
    startStatusUpdates();
});

// Tab-Navigation
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Tabs aktualisieren
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    // Tab-spezifische Aktionen
    if (tabName === 'status') {
        loadStatus();
    } else if (tabName === 'services') {
        loadServicesStatus();
    }
}

// Status laden
async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        updateStatusDisplay(data);
    } catch (error) {
        console.error('Fehler beim Laden des Status:', error);
    }
}

function updateStatusDisplay(status) {
    // Cluster Status
    document.getElementById('cluster-nodes').textContent = status.cluster?.nodes || 0;
    document.getElementById('cluster-cpus').textContent = status.cluster?.cpus || 0;
    document.getElementById('cluster-gpus').textContent = status.cluster?.gpus || 0;
    
    // Services Status
    updateServiceStatus('face-detection', status.services?.face_detection);
    updateServiceStatus('embedding', status.services?.embedding);
    updateServiceStatus('llm', status.services?.llm);
    updateServiceStatus('minio', status.services?.minio);
    updateServiceStatus('neo4j', status.services?.neo4j);
    
    // System Status
    document.getElementById('system-ram').textContent = formatBytes(status.system?.ram || 0);
    document.getElementById('system-disk').textContent = formatBytes(status.system?.disk || 0);
}

function updateServiceStatus(serviceId, status) {
    const element = document.getElementById(`status-${serviceId}`);
    if (element) {
        const indicator = element.querySelector('.status-indicator');
        const text = element.querySelector('.status-text');
        
        if (status?.online) {
            indicator.className = 'status-indicator online';
            text.textContent = 'Online';
        } else {
            indicator.className = 'status-indicator offline';
            text.textContent = 'Offline';
        }
    }
}

// Status-Updates starten
function startStatusUpdates() {
    statusInterval = setInterval(loadStatus, 5000); // Alle 5 Sekunden
}

// Installation
async function startInstallation() {
    const logOutput = document.getElementById('install-log');
    logOutput.innerHTML = '';
    
    const btn = document.getElementById('btn-install');
    btn.disabled = true;
    btn.innerHTML = 'Installiere... <span class="loading"></span>';
    
    try {
        const response = await fetch(`${API_BASE}/install`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const text = decoder.decode(value);
            const lines = text.split('\n');
            
            lines.forEach(line => {
                if (line.trim()) {
                    addLogLine(logOutput, line);
                }
            });
        }
        
        btn.disabled = false;
        btn.innerHTML = 'Installation starten';
        showAlert('Installation erfolgreich abgeschlossen!', 'success');
        
    } catch (error) {
        console.error('Installationsfehler:', error);
        addLogLine(logOutput, `Fehler: ${error.message}`, 'error');
        btn.disabled = false;
        btn.innerHTML = 'Installation starten';
        showAlert('Installation fehlgeschlagen!', 'error');
    }
}

function addLogLine(container, line, type = 'info') {
    const logLine = document.createElement('div');
    logLine.className = `log-line log-${type}`;
    logLine.textContent = line;
    container.appendChild(logLine);
    container.scrollTop = container.scrollHeight;
}

// Services verwalten
async function startService(service) {
    try {
        const response = await fetch(`${API_BASE}/services/${service}/start`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showAlert(`Service ${service} gestartet`, 'success');
            loadServicesStatus();
        } else {
            showAlert(`Fehler: ${data.error}`, 'error');
        }
    } catch (error) {
        showAlert(`Fehler: ${error.message}`, 'error');
    }
}

async function stopService(service) {
    try {
        const response = await fetch(`${API_BASE}/services/${service}/stop`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showAlert(`Service ${service} gestoppt`, 'success');
            loadServicesStatus();
        } else {
            showAlert(`Fehler: ${data.error}`, 'error');
        }
    } catch (error) {
        showAlert(`Fehler: ${error.message}`, 'error');
    }
}

async function loadServicesStatus() {
    try {
        const response = await fetch(`${API_BASE}/services/status`);
        const data = await response.json();
        
        // Update Service Status
        Object.keys(data).forEach(service => {
            updateServiceStatus(service, { online: data[service] });
        });
    } catch (error) {
        console.error('Fehler beim Laden des Service-Status:', error);
    }
}

// VLAN Setup
async function setupVLAN(nodeType, managementIP, workerIP, storageIP) {
    const logOutput = document.getElementById('vlan-log');
    logOutput.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE}/vlan/setup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                node_type: nodeType,
                management_ip: managementIP,
                worker_ip: workerIP,
                storage_ip: storageIP
            })
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const text = decoder.decode(value);
            const lines = text.split('\n');
            
            lines.forEach(line => {
                if (line.trim()) {
                    addLogLine(logOutput, line);
                }
            });
        }
        
        showAlert('VLAN Setup erfolgreich!', 'success');
        
    } catch (error) {
        console.error('VLAN Setup Fehler:', error);
        showAlert(`Fehler: ${error.message}`, 'error');
    }
}

// Konfiguration speichern
async function saveConfig(configType, config) {
    try {
        const response = await fetch(`${API_BASE}/config/${configType}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Konfiguration gespeichert!', 'success');
        } else {
            showAlert(`Fehler: ${data.error}`, 'error');
        }
    } catch (error) {
        showAlert(`Fehler: ${error.message}`, 'error');
    }
}

// Konfiguration laden
async function loadConfig(configType) {
    try {
        const response = await fetch(`${API_BASE}/config/${configType}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Fehler beim Laden der Konfiguration:', error);
        return null;
    }
}

// Helper Functions
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alert, container.firstChild);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Event Listeners
document.getElementById('btn-install')?.addEventListener('click', startInstallation);

// Service Buttons
document.querySelectorAll('[data-service-start]').forEach(btn => {
    btn.addEventListener('click', () => {
        startService(btn.dataset.serviceStart);
    });
});

document.querySelectorAll('[data-service-stop]').forEach(btn => {
    btn.addEventListener('click', () => {
        stopService(btn.dataset.serviceStop);
    });
});

// VLAN Setup Form
document.getElementById('vlan-setup-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    setupVLAN(
        formData.get('node_type'),
        formData.get('management_ip'),
        formData.get('worker_ip'),
        formData.get('storage_ip')
    );
});
