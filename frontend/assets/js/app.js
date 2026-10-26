/**
 * NetGuard IDS - Dashboard Application
 * Pure Vanilla JavaScript - No Dependencies
 */

// === Configuration ===
const API_BASE_URL = 'http://localhost:8000/api';
const REFRESH_INTERVAL = 5000; // 5 seconds
let refreshTimer = null;

// === DOM Elements ===
const elements = {
    // Status
    statusIndicator: document.getElementById('statusIndicator'),
    statusText: document.getElementById('statusText'),

    // Stats
    totalAlerts: document.getElementById('totalAlerts'),
    todayAlerts: document.getElementById('todayAlerts'),
    hourAlerts: document.getElementById('hourAlerts'),
    criticalAlerts: document.getElementById('criticalAlerts'),

    // Alerts
    alertsList: document.getElementById('alertsList'),
    loadingState: document.getElementById('loadingState'),
    emptyState: document.getElementById('emptyState'),
    errorState: document.getElementById('errorState'),

    // Footer
    lastUpdated: document.getElementById('lastUpdated'),

    // Buttons
    refreshBtn: document.getElementById('refreshBtn')
};

// === State Management ===
let appState = {
    isOnline: false,
    isLoading: true,
    alerts: [],
    stats: null,
    lastUpdateTime: null
};

// === API Functions ===
const api = {
    /**
     * Fetch data from API
     */
    async fetchData(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Get alerts
     */
    async getAlerts(limit = 50) {
        return await this.fetchData(`/alerts?limit=${limit}`);
    },

    /**
     * Get statistics
     */
    async getStats() {
        return await this.fetchData('/stats');
    },

    /**
     * Check health
     */
    async checkHealth() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            return response.ok;
        } catch (error) {
            return false;
        }
    }
};

// === UI Update Functions ===
const ui = {
    /**
     * Update status indicator
     */
    updateStatus(isOnline) {
        appState.isOnline = isOnline;

        if (isOnline) {
            elements.statusIndicator.classList.add('online');
            elements.statusText.textContent = 'System Online';
        } else {
            elements.statusIndicator.classList.remove('online');
            elements.statusText.textContent = 'System Offline';
        }
    },

    /**
     * Update statistics cards
     */
    updateStats(stats) {
        if (!stats) return;

        // Animate number changes
        this.animateValue(elements.totalAlerts, parseInt(elements.totalAlerts.textContent) || 0, stats.total_alerts || 0, 500);
        this.animateValue(elements.todayAlerts, parseInt(elements.todayAlerts.textContent) || 0, stats.alerts_today || 0, 500);
        this.animateValue(elements.hourAlerts, parseInt(elements.hourAlerts.textContent) || 0, stats.alerts_last_hour || 0, 500);
        this.animateValue(elements.criticalAlerts, parseInt(elements.criticalAlerts.textContent) || 0, stats.critical_alerts || 0, 500);

        appState.stats = stats;
    },

    /**
     * Animate number value
     */
    animateValue(element, start, end, duration) {
        if (start === end) return;

        const range = end - start;
        const increment = range / (duration / 16); // 60 FPS
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                element.textContent = end;
                clearInterval(timer);
            } else {
                element.textContent = Math.round(current);
            }
        }, 16);
    },

    /**
     * Update alerts list
     */
    updateAlerts(alerts) {
        appState.alerts = alerts;

        // Hide all states
        elements.loadingState.style.display = 'none';
        elements.emptyState.style.display = 'none';
        elements.errorState.style.display = 'none';

        if (alerts.length === 0) {
            elements.emptyState.style.display = 'block';
            return;
        }

        // Render alerts
        elements.alertsList.innerHTML = alerts.map(alert => this.createAlertCard(alert)).join('');
    },

    /**
     * Create alert card HTML
     */
    createAlertCard(alert) {
        const severity = this.getSeverityClass(alert.severity);
        const severityLabel = this.getSeverityLabel(alert.severity);
        const timestamp = this.formatTimestamp(alert.timestamp);

        return `
            <div class="alert-item ${severity}" data-alert-id="${alert.id}">
                <div class="alert-header">
                    <span class="alert-type">${this.escapeHtml(alert.type)}</span>
                    <span class="alert-badge ${severity}">${severityLabel}</span>
                </div>

                ${alert.description ? `
                    <p class="alert-description">${this.escapeHtml(alert.description)}</p>
                ` : ''}

                <div class="alert-details">
                    ${alert.source_ip ? `
                        <div class="alert-detail">
                            <svg class="alert-detail-icon" viewBox="0 0 16 16">
                                <circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
                                <path d="M8 3 L8 8 L11 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                            </svg>
                            <span>Source: ${this.escapeHtml(alert.source_ip)}</span>
                        </div>
                    ` : ''}

                    ${alert.target_ip ? `
                        <div class="alert-detail">
                            <svg class="alert-detail-icon" viewBox="0 0 16 16">
                                <circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
                                <circle cx="8" cy="8" r="2" fill="currentColor"/>
                            </svg>
                            <span>Target: ${this.escapeHtml(alert.target_ip)}${alert.target_port ? ':' + alert.target_port : ''}</span>
                        </div>
                    ` : ''}

                    ${alert.protocol ? `
                        <div class="alert-detail">
                            <span>Protocol: ${this.escapeHtml(alert.protocol)}</span>
                        </div>
                    ` : ''}

                    <div class="alert-detail">
                        <svg class="alert-detail-icon" viewBox="0 0 16 16">
                            <circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M8 4 L8 8 L11 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                        <span>${timestamp}</span>
                    </div>

                    ${alert.confidence ? `
                        <div class="alert-detail">
                            <span>Confidence: ${Math.round(alert.confidence * 100)}%</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    },

    /**
     * Get severity CSS class
     */
    getSeverityClass(severity) {
        if (severity >= 9) return 'critical';
        if (severity >= 7) return 'high';
        if (severity >= 5) return 'medium';
        return 'low';
    },

    /**
     * Get severity label
     */
    getSeverityLabel(severity) {
        if (severity >= 9) return 'Critical';
        if (severity >= 7) return 'High';
        if (severity >= 5) return 'Medium';
        return 'Low';
    },

    /**
     * Format timestamp
     */
    formatTimestamp(timestamp) {
        if (!timestamp) return 'Unknown';

        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;

        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;

        // Format as full date/time
        return date.toLocaleString();
    },

    /**
     * Show loading state
     */
    showLoading() {
        elements.loadingState.style.display = 'block';
        elements.emptyState.style.display = 'none';
        elements.errorState.style.display = 'none';
        elements.alertsList.innerHTML = '';
    },

    /**
     * Show error state
     */
    showError() {
        elements.loadingState.style.display = 'none';
        elements.emptyState.style.display = 'none';
        elements.errorState.style.display = 'block';
        elements.alertsList.innerHTML = '';
    },

    /**
     * Update last updated time
     */
    updateLastUpdated() {
        const now = new Date();
        elements.lastUpdated.textContent = now.toLocaleTimeString();
        appState.lastUpdateTime = now;
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// === Main Application Functions ===

/**
 * Load all data
 */
async function loadData() {
    try {
        appState.isLoading = true;

        // Check health first
        const isHealthy = await api.checkHealth();
        ui.updateStatus(isHealthy);

        if (!isHealthy) {
            ui.showError();
            return;
        }

        // Fetch data in parallel
        const [alerts, stats] = await Promise.all([
            api.getAlerts(),
            api.getStats()
        ]);

        // Update UI
        ui.updateStats(stats);
        ui.updateAlerts(alerts);
        ui.updateLastUpdated();

        appState.isLoading = false;

    } catch (error) {
        console.error('Error loading data:', error);
        ui.showError();
        ui.updateStatus(false);
        appState.isLoading = false;
    }
}

/**
 * Start auto-refresh
 */
function startAutoRefresh() {
    // Clear existing timer
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }

    // Load data immediately
    loadData();

    // Set up interval
    refreshTimer = setInterval(() => {
        if (!appState.isLoading) {
            loadData();
        }
    }, REFRESH_INTERVAL);

    console.log(`Auto-refresh started (every ${REFRESH_INTERVAL / 1000}s)`);
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
        console.log('Auto-refresh stopped');
    }
}

/**
 * Initialize application
 */
function initApp() {
    console.log('🛡️ NetGuard IDS Dashboard initialized');

    // Start auto-refresh
    startAutoRefresh();

    // Handle visibility change (pause when tab is hidden)
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            stopAutoRefresh();
        } else {
            startAutoRefresh();
        }
    });

    // Handle window unload
    window.addEventListener('beforeunload', () => {
        stopAutoRefresh();
    });

    console.log('✅ Dashboard ready');
}

// === Initialize on DOM load ===
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

// === Export for debugging ===
window.NetGuardIDS = {
    loadData,
    startAutoRefresh,
    stopAutoRefresh,
    state: appState,
    api,
    ui
};
