// Admin Dashboard JavaScript

const API_BASE = '/api';

// Status-Updates
let statusInterval = null;

// Initialisierung
document.addEventListener('DOMContentLoaded', () => {
    try {
        initTabs();
        loadStatus();
        startStatusUpdates();
        loadNodeType();
        initNodeTypeSelection();
        
        // Stelle sicher, dass der Overview-Tab sichtbar ist
        const overviewTab = document.getElementById('tab-overview');
        if (overviewTab) {
            overviewTab.classList.add('active');
        }
    } catch (error) {
        console.error('Fehler bei der Initialisierung:', error);
    }
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
        updateServicesForNodeType();
    } else if (tabName === 'node-setup') {
        loadNodeType();
    } else if (tabName === 'config') {
        loadConfigFromFile();
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
    const nodesEl = document.getElementById('cluster-nodes');
    const cpusEl = document.getElementById('cluster-cpus');
    const gpusEl = document.getElementById('cluster-gpus');
    if (nodesEl) nodesEl.textContent = status.cluster?.nodes || 0;
    if (cpusEl) cpusEl.textContent = status.cluster?.cpus || 0;
    if (gpusEl) gpusEl.textContent = status.cluster?.gpus || 0;
    
    // Services Status
    updateServiceStatus('face-detection', status.services?.face_detection);
    updateServiceStatus('embedding', status.services?.embedding);
    updateServiceStatus('llm', status.services?.llm);
    updateServiceStatus('minio', status.services?.minio);
    updateServiceStatus('neo4j', status.services?.neo4j);
    
    // System Status
    const ramEl = document.getElementById('system-ram');
    const diskEl = document.getElementById('system-disk');
    if (ramEl) ramEl.textContent = formatBytes(status.system?.ram || 0);
    if (diskEl) diskEl.textContent = formatBytes(status.system?.disk || 0);
}

function updateServiceStatus(serviceId, status) {
    const element = document.getElementById(`status-${serviceId}`);
    if (element) {
        const indicator = element.querySelector('.status-indicator');
        const text = element.querySelector('.status-text');
        
        if (indicator && text) {
            if (status && (status.online === true || status === true)) {
                indicator.className = 'status-indicator online';
                if (text) text.textContent = 'Online';
            } else {
                indicator.className = 'status-indicator offline';
                if (text) text.textContent = 'Offline';
            }
        }
    }
    
    // Update auch die Service-Status-Indikatoren in anderen Tabs
    const indicatorEl = document.getElementById(`status-${serviceId}-indicator`);
    const textEl = document.getElementById(`status-${serviceId}-text`);
    if (indicatorEl && textEl) {
        if (status && (status.online === true || status === true)) {
            indicatorEl.className = 'status-indicator online';
            textEl.textContent = 'Online';
        } else {
            indicatorEl.className = 'status-indicator offline';
            textEl.textContent = 'Offline';
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

// Node Type Management
let currentNodeType = 'management';

async function loadNodeType() {
    try {
        const response = await fetch(`${API_BASE}/node/type`);
        const data = await response.json();
        currentNodeType = data.node_type || 'management';
        
        // Update UI
        document.getElementById('current-node-type').textContent = 
            currentNodeType.charAt(0).toUpperCase() + currentNodeType.slice(1);
        document.getElementById('services-node-type').textContent = 
            currentNodeType.charAt(0).toUpperCase() + currentNodeType.slice(1);
        
        // Mark selected card
        document.querySelectorAll('.node-type-card').forEach(card => {
            if (card.dataset.nodeType === currentNodeType) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
        
        updateServicesForNodeType();
    } catch (error) {
        console.error('Fehler beim Laden des Node-Typs:', error);
    }
}

function initNodeTypeSelection() {
    document.querySelectorAll('.node-type-card').forEach(card => {
        card.addEventListener('click', () => {
            const nodeType = card.dataset.nodeType;
            document.querySelectorAll('.node-type-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            document.getElementById('btn-save-node-type').style.display = 'block';
            currentNodeType = nodeType;
        });
    });
    
    document.getElementById('btn-save-node-type')?.addEventListener('click', async () => {
        try {
            const response = await fetch(`${API_BASE}/node/type`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ node_type: currentNodeType })
            });
            
            const data = await response.json();
            if (data.success) {
                showAlert(`Node-Typ auf ${currentNodeType} gesetzt!`, 'success');
                document.getElementById('btn-save-node-type').style.display = 'none';
                loadNodeType();
            } else {
                showAlert(`Fehler: ${data.error}`, 'error');
            }
        } catch (error) {
            showAlert(`Fehler: ${error.message}`, 'error');
        }
    });
}

function updateServicesForNodeType() {
    // Zeige/Verstecke Services basierend auf Node-Typ
    const faceDetectionEl = document.getElementById('service-face-detection');
    const embeddingEl = document.getElementById('service-embedding');
    const llmEl = document.getElementById('service-llm');
    
    if (faceDetectionEl) faceDetectionEl.style.display = (currentNodeType === 'worker') ? 'block' : 'none';
    if (embeddingEl) embeddingEl.style.display = (currentNodeType === 'worker') ? 'block' : 'none';
    if (llmEl) llmEl.style.display = (currentNodeType === 'management') ? 'block' : 'none';
}

// Service Management für Node-Typ
async function startAllServicesForNode() {
    const logOutput = document.createElement('div');
    logOutput.className = 'log-output';
    logOutput.id = 'services-start-log';
    
    const servicesTab = document.getElementById('tab-services');
    const existingLog = document.getElementById('services-start-log');
    if (existingLog) existingLog.remove();
    servicesTab.appendChild(logOutput);
    
    try {
        const response = await fetch(`${API_BASE}/services/start-all`, {
            method: 'POST'
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
        
        showAlert('Services gestartet!', 'success');
        setTimeout(() => {
            loadServicesStatus();
            loadStatus();
        }, 2000);
        
    } catch (error) {
        console.error('Fehler beim Starten der Services:', error);
        addLogLine(logOutput, `Fehler: ${error.message}`, 'error');
        showAlert('Fehler beim Starten der Services!', 'error');
    }
}

async function stopAllServicesForNode() {
    const logOutput = document.createElement('div');
    logOutput.className = 'log-output';
    logOutput.id = 'services-stop-log';
    
    const servicesTab = document.getElementById('tab-services');
    const existingLog = document.getElementById('services-stop-log');
    if (existingLog) existingLog.remove();
    servicesTab.appendChild(logOutput);
    
    try {
        const response = await fetch(`${API_BASE}/services/stop-all`, {
            method: 'POST'
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
        
        showAlert('Services gestoppt!', 'success');
        setTimeout(() => {
            loadServicesStatus();
            loadStatus();
        }, 2000);
        
    } catch (error) {
        console.error('Fehler beim Stoppen der Services:', error);
        addLogLine(logOutput, `Fehler: ${error.message}`, 'error');
        showAlert('Fehler beim Stoppen der Services!', 'error');
    }
}

// Config Management
async function loadConfigFromFile() {
    const configType = document.getElementById('config-type-select').value;
    try {
        const config = await loadConfig(configType);
        if (config) {
            if (configType === 'pipeline') {
                // Update form fields
                const form = document.getElementById('pipeline-config-form');
                if (form) {
                    if (config.services?.face_detection?.url) {
                        form.querySelector('[name="face_detection_url"]').value = config.services.face_detection.url;
                    }
                    if (config.services?.embedding?.url) {
                        form.querySelector('[name="embedding_url"]').value = config.services.embedding.url;
                    }
                    if (config.services?.llm?.url) {
                        form.querySelector('[name="llm_url"]').value = config.services.llm.url;
                    }
                    if (config.minio?.endpoint) {
                        form.querySelector('[name="minio_endpoint"]').value = config.minio.endpoint;
                    }
                    if (config.neo4j?.uri) {
                        form.querySelector('[name="neo4j_uri"]').value = config.neo4j.uri;
                    }
                }
            }
            
            // Show YAML view
            const yamlView = document.getElementById('config-yaml-view');
            const yamlText = document.getElementById('config-yaml-text');
            if (yamlView && yamlText) {
                yamlText.value = JSON.stringify(config, null, 2);
                yamlView.style.display = 'block';
            }
            
            showAlert('Konfiguration geladen!', 'success');
        }
    } catch (error) {
        showAlert(`Fehler: ${error.message}`, 'error');
    }
}

async function saveConfigToFile() {
    const configType = document.getElementById('config-type-select').value;
    try {
        let config = {};
        
        if (configType === 'pipeline') {
            const form = document.getElementById('pipeline-config-form');
            if (form) {
                const formData = new FormData(form);
                config = {
                    services: {
                        face_detection: { url: formData.get('face_detection_url') },
                        embedding: { url: formData.get('embedding_url') },
                        llm: { url: formData.get('llm_url') }
                    },
                    minio: { endpoint: formData.get('minio_endpoint') },
                    neo4j: { uri: formData.get('neo4j_uri') }
                };
            }
        } else {
            // For other config types, use YAML text if available
            const yamlText = document.getElementById('config-yaml-text');
            if (yamlText && yamlText.value) {
                config = JSON.parse(yamlText.value);
            }
        }
        
        await saveConfig(configType, config);
        showAlert('Konfiguration gespeichert!', 'success');
    } catch (error) {
        showAlert(`Fehler: ${error.message}`, 'error');
    }
}
