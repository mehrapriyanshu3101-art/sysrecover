let memoryChart = null;

function initMemory() {
    initializeMemoryForm();
    initializeAutoImport();
}

function initializeMemoryForm() {
    const form = document.getElementById('memory-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const referenceString = document.getElementById('reference-string').value
            .split(',')
            .map(s => parseInt(s.trim()))
            .filter(n => !isNaN(n));
        
        const numFrames = parseInt(document.getElementById('num-frames').value);
        const algorithm = document.getElementById('memory-algorithm').value;
        
        if (referenceString.length === 0) {
            alert('Please enter a valid reference string');
            return;
        }
        
        fetch(`/api/runs/${activeRunId || 1}/memory/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                reference_string: referenceString,
                num_frames: numFrames,
                algorithm: algorithm
            })
        })
        .then(response => response.json())
        .then(data => {
            displayMemoryResults(data);
        })
        .catch(error => {
            console.error('Error running memory simulation:', error);
            alert('Error running memory simulation');
        });
    });
}

function initializeAutoImport() {
    const autoImportBtn = document.getElementById('auto-import-memory-btn');
    
    autoImportBtn.addEventListener('click', function() {
        if (!activeRunId) {
            alert('Please select a simulation run first');
            return;
        }
        
        autoImportBtn.disabled = true;
        autoImportBtn.innerHTML = '<i class="bi bi-spinner spin"></i> Generating...';
        
        fetch(`/api/runs/${activeRunId}/memory/auto-import`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('reference-string').value = data.reference_string.join(',');
            document.getElementById('num-frames').value = data.num_frames;
            alert(`Generated reference string from system memory patterns.\nSystem Memory: ${data.system_info.total_gb.toFixed(1)} GB total, ${data.system_info.used_percent}% used`);
        })
        .catch(error => {
            console.error('Error auto-generating memory reference:', error);
            alert('Error auto-generating memory reference');
        })
        .finally(() => {
            autoImportBtn.disabled = false;
            autoImportBtn.innerHTML = '<i class="bi bi-magic"></i> Auto-Generate from System';
        });
    });
}

function displayMemoryResults(data) {
    // Display results
    const resultsDiv = document.getElementById('memory-results');
    resultsDiv.innerHTML = `
        <p><strong>Algorithm:</strong> ${data.algorithm}</p>
        <p><strong>Page Faults:</strong> ${data.page_faults}</p>
        <p><strong>Hit Ratio:</strong> ${(data.hit_ratio * 100).toFixed(2)}%</p>
    `;
    
    // Display steps table
    const stepsTable = document.getElementById('memory-steps');
    stepsTable.innerHTML = data.steps.map(step => `
        <tr>
            <td>${step.step}</td>
            <td>${step.page}</td>
            <td>${step.frames.join(', ')}</td>
            <td><span class="badge badge-${step.fault ? 'danger' : 'success'}">${step.fault ? 'Fault' : 'Hit'}</span></td>
        </tr>
    `).join('');
    
    // Display chart
    displayMemoryChart(data.steps);
}

function displayMemoryChart(steps) {
    const ctx = document.getElementById('memoryChart');
    if (!ctx) return;
    
    if (memoryChart) {
        memoryChart.destroy();
    }
    
    const labels = steps.map(s => `Step ${s.step}`);
    const faultData = steps.map(s => s.fault ? 1 : 0);
    
    memoryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Page Fault',
                data: faultData,
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 1,
                    ticks: {
                        callback: function(value) {
                            return value === 1 ? 'Fault' : 'Hit';
                        }
                    }
                }
            }
        }
    });
}
