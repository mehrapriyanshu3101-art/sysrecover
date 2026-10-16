function initResources() {
    initializeResourceForm();
    initializeLockForm();
    loadResources();
    loadTransactions();
    loadLocks();
}

function initializeResourceForm() {
    const form = document.getElementById('resource-form');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!activeRunId) {
            alert('Please select a simulation run first');
            return;
        }
        
        const resourceName = document.getElementById('resource-name').value;
        const resourceType = document.getElementById('resource-type').value;
        const totalInstances = parseInt(document.getElementById('total-instances').value);
        
        fetch(`/api/runs/${activeRunId}/resources`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                resource_name: resourceName,
                resource_type: resourceType,
                total_instances: totalInstances
            })
        })
        .then(response => response.json())
        .then(data => {
            loadResources();
            form.reset();
            alert('Resource created successfully');
        })
        .catch(error => {
            console.error('Error creating resource:', error);
            alert('Error creating resource');
        });
    });
}

function initializeLockForm() {
    const form = document.getElementById('lock-form');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const transactionId = parseInt(document.getElementById('lock-transaction').value);
        const resourceId = parseInt(document.getElementById('lock-resource').value);
        const lockType = document.getElementById('lock-type').value;
        
        if (!transactionId || !resourceId) {
            alert('Please select both transaction and resource');
            return;
        }
        
        alert('Lock request functionality - backend implementation pending');
    });
}

function loadResources() {
    if (!activeRunId) {
        const table = document.getElementById('resources-table');
        table.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Please select a simulation run first</td></tr>';
        return;
    }
    
    fetch(`/api/runs/${activeRunId}/resources`)
        .then(response => response.json())
        .then(resources => {
            const table = document.getElementById('resources-table');
            const select = document.getElementById('lock-resource');
            
            if (resources.length > 0) {
                table.innerHTML = resources.map(r => `
                    <tr>
                        <td>${r.resource_name}</td>
                        <td>${r.resource_type}</td>
                        <td>${r.total_instances}</td>
                        <td>${r.available_instances}</td>
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="deleteResource(${r.resource_id})">Delete</button>
                        </td>
                    </tr>
                `).join('');
                
                select.innerHTML = '<option value="">Select resource</option>' + 
                    resources.map(r => `<option value="${r.resource_id}">${r.resource_name}</option>`).join('');
            } else {
                table.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No resources yet. Create one to get started.</td></tr>';
                select.innerHTML = '<option value="">Select resource</option>';
            }
        })
        .catch(error => {
            console.error('Error loading resources:', error);
        });
}

function loadTransactions() {
    console.log('loadTransactions called, activeRunId:', activeRunId);
    
    if (!activeRunId) {
        const select = document.getElementById('lock-transaction');
        if (select) {
            select.innerHTML = '<option value="">Select a simulation run first</option>';
        }
        return;
    }
    
    const url = `/api/runs/${activeRunId}/transactions`;
    console.log('Fetching transactions from:', url);
    
    fetch(url)
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(transactions => {
            console.log('Transactions received:', transactions);
            const select = document.getElementById('lock-transaction');
            if (!select) {
                console.error('Transaction select element not found');
                return;
            }
            
            if (transactions.length > 0) {
                select.innerHTML = '<option value="">Select transaction</option>' + 
                    transactions.map(t => `<option value="${t.transaction_id}">T${t.transaction_id} (${t.status})</option>`).join('');
            } else {
                select.innerHTML = '<option value="">No transactions available</option>';
            }
        })
        .catch(error => {
            console.error('Error loading transactions:', error);
            const select = document.getElementById('lock-transaction');
            if (select) {
                select.innerHTML = '<option value="">Error loading transactions</option>';
            }
        });
}

function loadLocks() {
    if (!activeRunId) {
        const table = document.getElementById('locks-table');
        table.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Please select a simulation run first</td></tr>';
        return;
    }
    
    const table = document.getElementById('locks-table');
    table.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Lock loading to be implemented</td></tr>';
}

function deleteResource(resourceId) {
    if (!confirm('Are you sure you want to delete this resource?')) {
        return;
    }
    
    alert('Resource deletion - backend implementation pending');
}
