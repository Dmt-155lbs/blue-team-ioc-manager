/**
 * IOC Manager - Frontend Application
 * Handles API communication and UI rendering
 */

// API Configuration
const API_BASE_URL = window.location.origin;

// ==================== API Functions ====================

/**
 * Fetch all threats from the API with optional filters
 */
async function fetchThreats(type = '', severity = '') {
    let url = `${API_BASE_URL}/api/threats?`;
    if (type) url += `type=${encodeURIComponent(type)}&`;
    if (severity) url += `severity=${encodeURIComponent(severity)}&`;
    
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

/**
 * Fetch threat statistics
 */
async function fetchStats() {
    const response = await fetch(`${API_BASE_URL}/api/threats/stats/summary`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

/**
 * Create a new threat
 */
async function createThreat(threatData) {
    const response = await fetch(`${API_BASE_URL}/api/threats`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(threatData),
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error creating threat');
    }
    return await response.json();
}

/**
 * Delete a threat by ID
 */
async function deleteThreat(threatId) {
    const response = await fetch(`${API_BASE_URL}/api/threats/${threatId}`, {
        method: 'DELETE',
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error deleting threat');
    }
    return await response.json();
}

// ==================== UI Functions ====================

/**
 * Show alert message
 */
function showAlert(message, type = 'success') {
    const container = document.getElementById('alert-container');
    const alertId = `alert-${Date.now()}`;
    
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

/**
 * Get severity badge HTML
 */
function getSeverityBadge(severity) {
    const badges = {
        'High': 'bg-danger',
        'Medium': 'bg-warning text-dark',
        'Low': 'bg-info'
    };
    const badgeClass = badges[severity] || 'bg-secondary';
    return `<span class="badge ${badgeClass}">${severity}</span>`;
}

/**
 * Get type icon
 */
function getTypeIcon(type) {
    const icons = {
        'IP': 'bi-hdd-network',
        'Hash': 'bi-file-binary',
        'URL': 'bi-link-45deg',
        'Domain': 'bi-globe'
    };
    return icons[type] || 'bi-question-circle';
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Render threats table
 */
function renderThreatsTable(threats) {
    const tbody = document.getElementById('threats-table-body');
    
    if (threats.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4 text-muted">
                    <i class="bi bi-inbox fs-1"></i>
                    <p class="mt-2 mb-0">No se encontraron indicadores</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = threats.map(threat => `
        <tr>
            <td><code>#${threat.id}</code></td>
            <td>
                <i class="bi ${getTypeIcon(threat.type)} me-1"></i>
                ${threat.type}
            </td>
            <td>
                <code class="text-break">${escapeHtml(threat.value)}</code>
            </td>
            <td>${getSeverityBadge(threat.severity)}</td>
            <td>${threat.source || '<span class="text-muted">-</span>'}</td>
            <td><small>${formatDate(threat.date_detected)}</small></td>
            <td>
                <button class="btn btn-sm btn-outline-danger" onclick="handleDelete(${threat.id})" title="Eliminar">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

/**
 * Update statistics cards
 */
function updateStats(stats) {
    document.getElementById('stat-total').textContent = stats.total || 0;
    document.getElementById('stat-high').textContent = stats.by_severity?.High || 0;
    document.getElementById('stat-medium').textContent = stats.by_severity?.Medium || 0;
    document.getElementById('stat-low').textContent = stats.by_severity?.Low || 0;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== Event Handlers ====================

/**
 * Load threats with current filters
 */
async function loadThreats() {
    const type = document.getElementById('filter-type').value;
    const severity = document.getElementById('filter-severity').value;
    
    try {
        const [threats, stats] = await Promise.all([
            fetchThreats(type, severity),
            fetchStats()
        ]);
        
        renderThreatsTable(threats);
        updateStats(stats);
    } catch (error) {
        console.error('Error loading threats:', error);
        showAlert('Error al cargar los indicadores: ' + error.message, 'danger');
        
        document.getElementById('threats-table-body').innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4 text-danger">
                    <i class="bi bi-exclamation-triangle fs-1"></i>
                    <p class="mt-2 mb-0">Error al conectar con la API</p>
                </td>
            </tr>
        `;
    }
}

/**
 * Clear all filters
 */
function clearFilters() {
    document.getElementById('filter-type').value = '';
    document.getElementById('filter-severity').value = '';
    loadThreats();
}

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const threatData = {
        type: document.getElementById('ioc-type').value,
        value: document.getElementById('ioc-value').value.trim(),
        severity: document.getElementById('ioc-severity').value,
        source: document.getElementById('ioc-source').value.trim() || null
    };
    
    try {
        const result = await createThreat(threatData);
        showAlert(`IOC registrado exitosamente (ID: ${result.id})`, 'success');
        
        // Clear form
        document.getElementById('ioc-value').value = '';
        document.getElementById('ioc-source').value = '';
        
        // Reload table
        loadThreats();
    } catch (error) {
        console.error('Error creating threat:', error);
        showAlert('Error al registrar IOC: ' + error.message, 'danger');
    }
}

/**
 * Handle delete button click
 */
async function handleDelete(threatId) {
    if (!confirm(`¿Está seguro de eliminar el IOC #${threatId}?`)) {
        return;
    }
    
    try {
        await deleteThreat(threatId);
        showAlert(`IOC #${threatId} eliminado exitosamente`, 'success');
        loadThreats();
    } catch (error) {
        console.error('Error deleting threat:', error);
        showAlert('Error al eliminar IOC: ' + error.message, 'danger');
    }
}

// ==================== Initialization ====================

document.addEventListener('DOMContentLoaded', () => {
    // Load initial data
    loadThreats();
    
    // Setup form handler
    document.getElementById('ioc-form').addEventListener('submit', handleFormSubmit);
    
    // Auto-refresh every 30 seconds
    setInterval(loadThreats, 30000);
});
