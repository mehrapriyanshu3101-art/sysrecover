function initEvents() {
    initializeFilters();
    loadEvents();
}

function initializeFilters() {
    const severityFilter = document.getElementById('filter-severity');
    const typeFilter = document.getElementById('filter-type');
    
    severityFilter.addEventListener('change', loadEvents);
    typeFilter.addEventListener('change', loadEvents);
}

function loadEvents() {
    if (!activeRunId) {
        const table = document.getElementById('events-table');
        table.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Please select a simulation run first</td></tr>';
        return;
    }
    
    const severity = document.getElementById('filter-severity').value;
    const eventType = document.getElementById('filter-type').value;
    
    let url = `/api/runs/${activeRunId}/events`;
    const params = [];
    if (severity) params.push(`severity=${severity}`);
    if (eventType) params.push(`event_type=${eventType}`);
    if (params.length > 0) url += '?' + params.join('&');
    
    fetch(url)
        .then(response => response.json())
        .then(events => {
            const table = document.getElementById('events-table');
            
            if (events.length > 0) {
                table.innerHTML = events.map(e => `
                    <tr>
                        <td>${new Date(e.timestamp).toLocaleString()}</td>
                        <td>${e.event_type}</td>
                        <td><span class="badge badge-${e.severity}">${e.severity}</span></td>
                        <td>${e.details || '-'}</td>
                    </tr>
                `).join('');
            } else {
                table.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No events found</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error loading events:', error);
            const table = document.getElementById('events-table');
            table.innerHTML = '<tr><td colspan="4" class="text-center text-danger">Error loading events</td></tr>';
        });
}
