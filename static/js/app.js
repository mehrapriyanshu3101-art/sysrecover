// Global state
let activeRunId = null;
let currentPage = 'dashboard';

// API base URL
const API_BASE = '/api';
const ACTIVE_RUN_KEY = 'sysrecover.activeRunId';

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    // Restore the run selected on a previous page
    const savedRunId = localStorage.getItem(ACTIVE_RUN_KEY);
    activeRunId = savedRunId ? parseInt(savedRunId) : null;

    currentPage = window.location.pathname.replace('/', '') || 'dashboard';

    initializeNavigation();
    initializeRunSelector();
    initializeNewRunModal();
    loadRuns();
    initializePageScripts(currentPage);
});

// Navigation
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            // Dashboard is at root path, not /dashboard
            window.location.href = page === 'dashboard' ? '/' : `/${page}`;
        });
    });
}

function setActiveRun(runId) {
    activeRunId = runId ? parseInt(runId) : null;

    if (activeRunId) {
        localStorage.setItem(ACTIVE_RUN_KEY, activeRunId);
    } else {
        localStorage.removeItem(ACTIVE_RUN_KEY);
    }

    const selector = document.getElementById('active-run-select');
    if (selector) {
        selector.value = activeRunId || '';
    }
}

function refreshPageData(page) {
    // Page-specific data refresh logic
    if (page === 'dashboard' && typeof loadDashboardMetrics === 'function') {
        loadDashboardMetrics();
    } else if (page === 'runs' && typeof loadRuns === 'function') {
        loadRuns();
    } else if (page === 'processes' && typeof loadProcesses === 'function') {
        loadProcesses();
    } else if (page === 'scheduling' && typeof loadScheduling === 'function') {
        loadScheduling();
    } else if (page === 'memory' && typeof loadMemory === 'function') {
        loadMemory();
    } else if (page === 'transactions' && typeof loadTransactions === 'function') {
        loadTransactions();
    } else if (page === 'resources' && typeof loadResources === 'function') {
        loadResources();
        if (typeof loadTransactions === 'function') loadTransactions();
        if (typeof loadLocks === 'function') loadLocks();
    } else if (page === 'deadlocks' && typeof detectDeadlock === 'function') {
        detectDeadlock();
    } else if (page === 'recovery' && typeof loadRecoveryData === 'function') {
        loadRecoveryData();
    } else if (page === 'diagnostics' && typeof runDiagnostics === 'function') {
        runDiagnostics();
    } else if (page === 'events' && typeof loadEvents === 'function') {
        loadEvents();
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
        }
    }, 100);
}

// Run Selector
function initializeRunSelector() {
    const selector = document.getElementById('active-run-select');
    if (!selector) return;

    selector.addEventListener('change', function() {
        setActiveRun(this.value || null);
        refreshPageData(currentPage);
    });
}

function loadRuns() {
    return fetch(`${API_BASE}/runs`)
        .then(response => response.json())
        .then(runs => {
            const selector = document.getElementById('active-run-select');
            if (!selector) return;

            selector.innerHTML = '<option value="">Select Simulation Run</option>';
            runs.forEach(run => {
                const option = document.createElement('option');
                option.value = run.run_id;
                option.textContent = run.name;
                selector.appendChild(option);
            });

            // Drop a remembered run that no longer exists
            if (activeRunId && !runs.some(run => run.run_id === activeRunId)) {
                setActiveRun(null);
                return;
            }

            if (activeRunId) {
                selector.value = activeRunId;
            }
        })
        .catch(error => console.error('Error loading runs:', error));
}

// New Run Modal
function initializeNewRunModal() {
    const modalElement = document.getElementById('newRunModal');
    const btn = document.getElementById('new-run-btn');
    const createBtn = document.getElementById('create-run-btn');
    if (!modalElement || !btn || !createBtn) return;

    const modal = new bootstrap.Modal(modalElement);

    btn.addEventListener('click', () => modal.show());

    createBtn.addEventListener('click', function() {
        const name = document.getElementById('run-name').value.trim();
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
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || 'Could not create run');
                });
            }
            return response.json();
        })
        .then(run => {
            modal.hide();
            document.getElementById('run-name').value = '';
            document.getElementById('run-description').value = '';

            setActiveRun(run.run_id);
            loadRuns().then(() => refreshPageData(currentPage));

            alert('Simulation run created successfully!');
        })
        .catch(error => {
            console.error('Error creating run:', error);
            alert(error.message || 'Error creating run');
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
