function initTransactions() {
    initializeTransactionForm();
    initializeOperationForm();
    initializeAutoGenerate();
    loadTransactions();
    loadDataStore();
}

function initializeTransactionForm() {
    const form = document.getElementById('transaction-form');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!activeRunId) {
            alert('Please select a simulation run first');
            return;
        }

        const type = document.getElementById('transaction-type').value;

        fetch(`/api/runs/${activeRunId}/transactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type })
        })
        .then(response => response.json())
        .then(data => {
            loadTransactions();
            alert('Transaction created successfully');
        })
        .catch(error => {
            console.error('Error creating transaction:', error);
            alert('Error creating transaction');
        });
    });
}

function initializeOperationForm() {
    const form = document.getElementById('operation-form');
    const operationType = document.getElementById('operation-type');
    const newValueGroup = document.getElementById('new-value-group');

    operationType.addEventListener('change', function() {
        newValueGroup.style.display = this.value === 'write' ? 'block' : 'none';
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const transactionId = parseInt(document.getElementById('select-transaction').value);
        const operation = document.getElementById('operation-type').value;
        const dataItem = document.getElementById('data-item').value;
        const newValue = document.getElementById('new-value').value;

        if (!transactionId) {
            alert('Please select a transaction');
            return;
        }

        if (operation === 'write' && newValue === '') {
            alert('Please enter a value to write');
            return;
        }

        fetch(`/api/transactions/${transactionId}/operations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                operation: operation,
                data_item: dataItem,
                new_value: newValue
            })
        })
        .then(response => response.json().then(body => ({ ok: response.ok, body })))
        .then(({ ok, body }) => {
            if (!ok) {
                alert(body.error || 'Operation failed');
                return;
            }

            if (body.data_store) {
                updateDataStore(body.data_store);
            }

            if (operation === 'read') {
                showAlert(`Read ${body.data_item} = ${body.value}`, 'info');
            } else {
                showAlert(`Wrote ${body.data_item}: ${body.old_value} to ${body.new_value} (LSN ${body.lsn})`, 'success');
            }
        })
        .catch(error => {
            console.error('Error executing operation:', error);
            alert('Error executing operation');
        });
    });
}

function loadDataStore() {
    fetch('/api/data-store')
        .then(response => response.json())
        .then(updateDataStore)
        .catch(error => console.error('Error loading data store:', error));
}

function updateDataStore(store) {
    const itemA = document.getElementById('data-A');
    const itemB = document.getElementById('data-B');
    if (itemA && store.A !== undefined) itemA.textContent = store.A;
    if (itemB && store.B !== undefined) itemB.textContent = store.B;
}

function initializeAutoGenerate() {
    const autoGenerateBtn = document.getElementById('auto-generate-transactions-btn');

    autoGenerateBtn.addEventListener('click', function() {
        if (!activeRunId) {
            alert('Please select a simulation run first');
            return;
        }

        if (!confirm('This will generate 5 realistic transactions automatically. Continue?')) {
            return;
        }

        autoGenerateBtn.disabled = true;
        autoGenerateBtn.innerHTML = '<i class="bi bi-spinner spin"></i> Generating...';

        fetch(`/api/runs/${activeRunId}/transactions/auto-generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            loadTransactions();
            alert(data.message);
        })
        .catch(error => {
            console.error('Error auto-generating transactions:', error);
            alert('Error auto-generating transactions');
        })
        .finally(() => {
            autoGenerateBtn.disabled = false;
            autoGenerateBtn.innerHTML = '<i class="bi bi-magic"></i> Auto-Generate Transactions';
        });
    });
}

function loadTransactions() {
    if (!activeRunId) {
        const table = document.getElementById('transactions-table');
        table.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Please select a simulation run first</td></tr>';
        return;
    }

    fetch(`/api/runs/${activeRunId}/transactions`)
        .then(response => response.json())
        .then(transactions => {
            const table = document.getElementById('transactions-table');
            const select = document.getElementById('select-transaction');

            if (transactions.length > 0) {
                table.innerHTML = transactions.map(t => `
                    <tr>
                        <td>${t.transaction_id}</td>
                        <td>${t.type}</td>
                        <td><span class="badge badge-${t.status === 'committed' ? 'success' : t.status === 'aborted' ? 'danger' : 'info'}">${t.status}</span></td>
                        <td>${t.two_phase_state}</td>
                        <td>
                            ${t.status === 'active' ? `
                                <button class="btn btn-sm btn-success" onclick="commitTransaction(${t.transaction_id})">Commit</button>
                                <button class="btn btn-sm btn-danger" onclick="rollbackTransaction(${t.transaction_id})">Rollback</button>
                            ` : '-'}
                        </td>
                    </tr>
                `).join('');

                select.innerHTML = '<option value="">Select a transaction</option>' +
                    transactions
                        .filter(t => t.status === 'active')
                        .map(t => `<option value="${t.transaction_id}">T${t.transaction_id}</option>`)
                        .join('');
            } else {
                table.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No transactions</td></tr>';
                select.innerHTML = '<option value="">Select a transaction</option>';
            }
        })
        .catch(error => console.error('Error loading transactions:', error));
}

function commitTransaction(transactionId) {
    fetch(`/api/transactions/${transactionId}/commit`, {
        method: 'POST'
    })
    .then(response => response.json().then(body => ({ ok: response.ok, body })))
    .then(({ ok, body }) => {
        if (!ok) {
            alert(body.error || 'Error committing transaction');
            return;
        }
        loadTransactions();
        alert('Transaction committed');
    })
    .catch(error => {
        console.error('Error committing transaction:', error);
        alert('Error committing transaction');
    });
}

function rollbackTransaction(transactionId) {
    fetch(`/api/transactions/${transactionId}/rollback`, {
        method: 'POST'
    })
    .then(response => response.json().then(body => ({ ok: response.ok, body })))
    .then(({ ok, body }) => {
        if (!ok) {
            alert(body.error || 'Error rolling back transaction');
            return;
        }
        loadTransactions();
        alert('Transaction rolled back');
    })
    .catch(error => {
        console.error('Error rolling back transaction:', error);
        alert('Error rolling back transaction');
    });
}
