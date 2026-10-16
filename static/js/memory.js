let memoryChart = null;

function initMemory() {
    initializeMemoryForm();
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
