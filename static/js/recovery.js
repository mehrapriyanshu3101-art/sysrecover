function initRecovery() {
    loadRecoveryData();
}

function loadRecoveryData() {
    if (!activeRunId) {
        return;
    }

    loadRecoveryLogs();
    loadCheckpoints();
}

function loadRecoveryLogs() {
    fetch(`/api/runs/${activeRunId}/recovery-logs`)
        .then(response => response.json())
        .then(logs => {
            const table = document.getElementById('recovery-log-table');

            if (logs.length > 0) {
                table.innerHTML = logs.map(log => `
                    <tr>
                        <td>${log.lsn}</td>
                        <td>T${log.transaction_id}</td>
                        <td>${log.operation}</td>
                        <td>${log.data_item || '-'}</td>
                        <td>${log.old_value !== null ? log.old_value : '-'}</td>
                        <td>${log.new_value !== null ? log.new_value : '-'}</td>
                    </tr>
                `).join('');
            } else {
                table.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No log entries</td></tr>';
            }
        })
        .catch(error => console.error('Error loading recovery logs:', error));
}

function loadCheckpoints() {
    fetch(`/api/runs/${activeRunId}/checkpoints`)
        .then(response => response.json())
        .then(checkpoints => {
            const table = document.getElementById('checkpoint-table');

            if (checkpoints.length > 0) {
                table.innerHTML = checkpoints.map(cp => `
                    <tr>
                        <td>${cp.checkpoint_id}</td>
                        <td>${cp.lsn}</td>
                        <td>${cp.timestamp ? new Date(cp.timestamp).toLocaleString() : '-'}</td>
                        <td>${cp.active_transactions || '[]'}</td>
                    </tr>
                `).join('');
            } else {
                table.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No checkpoints</td></tr>';
            }
        })
        .catch(error => console.error('Error loading checkpoints:', error));
}

function createCheckpoint() {
    if (!activeRunId) {
        alert('Please select a simulation run first');
        return;
    }

    fetch(`/api/runs/${activeRunId}/checkpoints`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        const statusDiv = document.getElementById('recovery-status');
        statusDiv.innerHTML = `
            <div class="alert alert-success">
                <strong>Checkpoint Created</strong><br>
                LSN: ${data.lsn}<br>
                Time: ${data.timestamp ? new Date(data.timestamp).toLocaleString() : '-'}
            </div>
        `;
        loadRecoveryData();
    })
    .catch(error => {
        console.error('Error creating checkpoint:', error);
        alert('Error creating checkpoint');
    });
}

function simulateCrash() {
    if (!activeRunId) {
        alert('Please select a simulation run first');
        return;
    }

    fetch(`/api/runs/${activeRunId}/crash`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        const statusDiv = document.getElementById('recovery-status');
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                <strong>Crash Simulated</strong><br>
                Affected transactions: ${data.affected_transactions}
            </div>
        `;
        loadRecoveryData();
    })
    .catch(error => {
        console.error('Error simulating crash:', error);
        alert('Error simulating crash');
    });
}

function performRecovery() {
    if (!activeRunId) {
        alert('Please select a simulation run first');
        return;
    }

    fetch(`/api/runs/${activeRunId}/recover`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        const statusDiv = document.getElementById('recovery-status');

        if (data.undo_count === undefined) {
            statusDiv.innerHTML = `
                <div class="alert alert-warning">
                    <strong>Recovery Needed</strong><br>
                    ${data.message}
                </div>
            `;
            return;
        }

        statusDiv.innerHTML = `
            <div class="alert alert-success">
                <strong>Recovery Completed</strong><br>
                Checkpoint LSN: ${data.checkpoint_lsn}<br>
                UNDO operations: ${data.undo_count}<br>
                REDO operations: ${data.redo_count}
            </div>
        `;
        loadRecoveryData();
    })
    .catch(error => {
        console.error('Error performing recovery:', error);
        alert('Error performing recovery');
    });
}
