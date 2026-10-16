function initDeadlocks() {
    // Initialize deadlock detection page
}

function detectDeadlock() {
    if (!activeRunId) {
        alert('Please select a simulation run first');
        return;
    }
    
    fetch(`/api/runs/${activeRunId}/deadlocks/detect`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        const statusDiv = document.getElementById('deadlock-status');
        const infoDiv = document.getElementById('deadlock-info');
        
        if (data.deadlock_detected) {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Deadlock Detected!</strong>
                </div>
            `;
            infoDiv.innerHTML = `
                <pre>${JSON.stringify(data.graph, null, 2)}</pre>
            `;
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <strong>No Deadlock</strong>
                </div>
            `;
            infoDiv.innerHTML = '<p class="text-muted">No deadlock detected in the system</p>';
        }
    })
    .catch(error => {
        console.error('Error detecting deadlock:', error);
        alert('Error detecting deadlock');
    });
}

function recoverDeadlock() {
    if (!activeRunId) {
        alert('Please select a simulation run first');
        return;
    }
    
    alert('Deadlock recovery - needs victim selection implementation');
}
