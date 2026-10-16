let activityChart = null;
let resourceChart = null;

function initDashboard() {
    loadDashboardMetrics();
}

function loadDashboardMetrics() {
    if (!activeRunId) {
        document.getElementById('metric-processes').textContent = '0';
        document.getElementById('metric-transactions').textContent = '0';
        document.getElementById('metric-status').textContent = '-';
        document.getElementById('metric-events').textContent = '0';
        return;
    }
    
    fetch(`/api/runs/${activeRunId}/dashboard`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('metric-processes').textContent = data.process_count;
            document.getElementById('metric-transactions').textContent = data.transaction_count;
            document.getElementById('metric-status').textContent = data.status;
            document.getElementById('metric-events').textContent = data.recent_events.length;
            
            // Update recent events table
            const eventsTable = document.getElementById('recent-events-table');
            if (data.recent_events.length > 0) {
                eventsTable.innerHTML = data.recent_events.map(e => `
                    <tr>
                        <td>${new Date(e.timestamp).toLocaleString()}</td>
                        <td>${e.event_type}</td>
                        <td><span class="badge badge-${e.severity}">${e.severity}</span></td>
                        <td>${e.details || '-'}</td>
                    </tr>
                `).join('');
            } else {
                eventsTable.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No events yet</td></tr>';
            }
            
            // Initialize charts
            initCharts();
        })
        .catch(error => {
            console.error('Error loading dashboard metrics:', error);
        });
}

function initCharts() {
    // Activity Chart
    const activityCtx = document.getElementById('activityChart');
    if (activityCtx) {
        if (activityChart) {
            activityChart.destroy();
        }
        activityChart = new Chart(activityCtx, {
            type: 'line',
            data: {
                labels: ['1h', '2h', '3h', '4h', '5h', '6h'],
                datasets: [{
                    label: 'Process Activity',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: '#0d6efd',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true
                    }
                }
            }
        });
    }
    
    // Resource Chart
    const resourceCtx = document.getElementById('resourceChart');
    if (resourceCtx) {
        if (resourceChart) {
            resourceChart.destroy();
        }
        resourceChart = new Chart(resourceCtx, {
            type: 'doughnut',
            data: {
                labels: ['CPU', 'Memory', 'I/O', 'Network'],
                datasets: [{
                    data: [30, 40, 20, 10],
                    backgroundColor: ['#0d6efd', '#198754', '#ffc107', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true
                    }
                }
            }
        });
    }
}
