function initProcesses() {
    initializeProcessForm();
    loadProcesses();
}

function initializeProcessForm() {
    const form = document.getElementById('process-form');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!activeRunId) {
            alert('Please select a simulation run first');
            return;
        }
        
        const name = document.getElementById('process-name').value;
        const arrivalTime = parseInt(document.getElementById('arrival-time').value);
        const burstTime = parseInt(document.getElementById('burst-time').value);
        const priority = parseInt(document.getElementById('priority').value);
        
        fetch(`/api/runs/${activeRunId}/processes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                arrival_time: arrivalTime,
                burst_time: burstTime,
                priority
            })
        })
        .then(response => response.json())
        .then(data => {
            loadProcesses();
            form.reset();
            alert('Process created successfully');
        })
        .catch(error => {
            console.error('Error creating process:', error);
            alert('Error creating process');
        });
    });
}

function loadProcesses() {
    if (!activeRunId) {
        const table = document.getElementById('processes-table');
        table.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Please select a simulation run first</td></tr>';
        return;
    }
    
    fetch(`/api/runs/${activeRunId}/processes`)
        .then(response => response.json())
        .then(processes => {
            const table = document.getElementById('processes-table');
            
            if (processes.length > 0) {
                table.innerHTML = processes.map(p => `
                    <tr>
                        <td>${p.process_id}</td>
                        <td>${p.name}</td>
                        <td>${p.arrival_time}</td>
                        <td>${p.burst_time}</td>
                        <td>${p.priority}</td>
                        <td><span class="badge badge-info">${p.state}</span></td>
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="deleteProcess(${p.process_id})">Delete</button>
                        </td>
                    </tr>
                `).join('');
            } else {
                table.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No processes yet. Add one to get started.</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error loading processes:', error);
            const table = document.getElementById('processes-table');
            table.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Error loading processes</td></tr>';
        });
}

function deleteProcess(processId) {
    if (!confirm('Are you sure you want to delete this process?')) {
        return;
    }
    
    fetch(`/api/processes/${processId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        loadProcesses();
        alert('Process deleted successfully');
    })
    .catch(error => {
        console.error('Error deleting process:', error);
        alert('Error deleting process');
    });
}
