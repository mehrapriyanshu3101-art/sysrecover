function initRuns() {
    loadRuns();
}

function loadRuns() {
    fetch('/api/runs')
        .then(response => response.json())
        .then(runs => {
            const table = document.getElementById('runs-table');
            
            if (runs.length > 0) {
                table.innerHTML = runs.map(run => `
                    <tr>
                        <td>${run.run_id}</td>
                        <td>${run.name}</td>
                        <td>${run.description || '-'}</td>
                        <td><span class="badge badge-${run.status === 'active' ? 'success' : 'info'}">${run.status}</span></td>
                        <td>${new Date(run.created_at).toLocaleString()}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="selectRun(${run.run_id})">Select</button>
                            <button class="btn btn-sm btn-warning" onclick="finishRun(${run.run_id})">Finish</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteRun(${run.run_id})">Delete</button>
                        </td>
                    </tr>
                `).join('');
            } else {
                table.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No simulation runs yet. Create one to get started.</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error loading runs:', error);
            const table = document.getElementById('runs-table');
            table.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error loading runs</td></tr>';
        });
}

function selectRun(runId) {
    activeRunId = runId;
    document.getElementById('active-run-select').value = runId;
    alert(`Run ${runId} selected`);
    loadRuns();
}

function finishRun(runId) {
    if (!confirm('Are you sure you want to finish this run?')) {
        return;
    }
    
    fetch(`/api/runs/${runId}/finish`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        loadRuns();
        alert('Run finished successfully');
    })
    .catch(error => {
        console.error('Error finishing run:', error);
        alert('Error finishing run');
    });
}

function deleteRun(runId) {
    if (!confirm('Are you sure you want to delete this run? This cannot be undone.')) {
        return;
    }
    
    fetch(`/api/runs/${runId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        loadRuns();
        if (activeRunId === runId) {
            activeRunId = null;
            document.getElementById('active-run-select').value = '';
        }
        alert('Run deleted successfully');
    })
    .catch(error => {
        console.error('Error deleting run:', error);
        alert('Error deleting run');
    });
}
