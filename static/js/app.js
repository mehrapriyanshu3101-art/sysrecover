// Global state
let activeRunId = null;
let currentPage = 'dashboard';

// API base URL
const API_BASE = '/api';

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeRunSelector();
    initializeNewRunModal();
    loadRuns();
    
    // Initialize page-specific scripts based on current URL
    const path = window.location.pathname.replace('/', '') || 'dashboard';
    initializePageScripts(path);
});

// Navigation
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            window.location.href = `/${page}`;
        });
    });
}

function refreshPageData(page) {
    // Page-specific data refresh logic
    if (page === 'dashboard' && typeof loadDashboardMetrics === 'function') {
        loadDashboardMetrics();
    }
}

function initializePageScripts(page) {
    // Update active nav link
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });
    
    // Update page title
    const titles = {
        'dashboard': 'Overview',
        'runs': 'Simulation Runs',
        'processes': 'Process Management',
        'scheduling': 'CPU Scheduling',
        'memory': 'Memory Management',
        'transactions': 'Transaction Management',
        'resources': 'Resources & Locks',
        'deadlocks': 'Deadlock Detection',
        'recovery': 'Crash Recovery',
        'diagnostics': 'Smart Diagnostics',
        'events': 'Event History',
        'reports': 'Reports',
        'about': 'About'
    };
    const titleElement = document.getElementById('page-title');
    if (titleElement) {
        titleElement.textContent = titles[page] || 'Overview';
    }
    
    // Initialize page-specific scripts with setTimeout to ensure DOM is ready
    setTimeout(() => {
        if (page === 'dashboard' && typeof initDashboard === 'function') {
            initDashboard();
        } else if (page === 'runs' && typeof initRuns === 'function') {
            initRuns();
        } else if (page === 'processes' && typeof initProcesses === 'function') {
            initProcesses();
        } else if (page === 'scheduling' && typeof initScheduling === 'function') {
            initScheduling();
        } else if (page === 'memory' && typeof initMemory === 'function') {
            initMemory();
        } else if (page === 'transactions' && typeof initTransactions === 'function') {
            initTransactions();
        } else if (page === 'resources' && typeof initResources === 'function') {
            initResources();
        } else if (page === 'deadlocks' && typeof initDeadlocks === 'function') {
            initDeadlocks();
        } else if (page === 'recovery' && typeof initRecovery === 'function') {
            initRecovery();
        } else if (page === 'diagnostics' && typeof initDiagnostics === 'function') {
            initDiagnostics();
        } else if (page === 'events' && typeof initEvents === 'function') {
            initEvents();
        } else if (page === 'reports' && typeof initReports === 'function') {
            initReports();
        }
    }, 100);
    
    // Refresh data if run is selected
    if (activeRunId) {
        refreshPageData(page);
    }
}

// Run Selector
function initializeRunSelector() {
    const selector = document.getElementById('active-run-select');
    selector.addEventListener('change', function() {
        activeRunId = this.value ? parseInt(this.value) : null;
        if (activeRunId) {
            refreshPageData(currentPage);
        }
    });
}

function loadRuns() {
    fetch(`${API_BASE}/runs`)
        .then(response => response.json())
        .then(runs => {
            const selector = document.getElementById('active-run-select');
            selector.innerHTML = '<option value="">Select Simulation Run</option>';
            runs.forEach(run => {
                const option = document.createElement('option');
                option.value = run.run_id;
                option.textContent = run.name;
                selector.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading runs:', error));
}

// New Run Modal
function initializeNewRunModal() {
    const modal = new bootstrap.Modal(document.getElementById('newRunModal'));
    const btn = document.getElementById('new-run-btn');
    const createBtn = document.getElementById('create-run-btn');
    
    btn.addEventListener('click', () => modal.show());
    
    createBtn.addEventListener('click', function() {
        const name = document.getElementById('run-name').value;
        const description = document.getElementById('run-description').value;
        
        if (!name) {
            alert('Please enter a run name');
            return;
        }
        
        fetch(`${API_BASE}/runs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        })
        .then(response => response.json())
        .then(run => {
            modal.hide();
            loadRuns();
            document.getElementById('run-name').value = '';
            document.getElementById('run-description').value = '';
            
            // Auto-select the new run
            activeRunId = run.run_id;
            document.getElementById('active-run-select').value = run.run_id;
            
            alert('Simulation run created successfully!');
        })
        .catch(error => {
            console.error('Error creating run:', error);
            alert('Error creating run');
        });
    });
}

// Helper function for API calls
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const defaultOptions = {
        headers: { 'Content-Type': 'application/json' }
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
}

// Helper to show alerts
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const pageContent = document.getElementById('page-content');
    pageContent.insertBefore(alertDiv, pageContent.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Global navigation helper
window.navigateTo = function(page) {
    window.location.href = `/${page}`;
};
