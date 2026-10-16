function initDiagnostics() {
    // Initialize diagnostics page
}

function runDiagnostics() {
    if (!activeRunId) {
        alert('Please select a simulation run first');
        return;
    }
    
    fetch(`/api/runs/${activeRunId}/diagnostics`)
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('diagnostics-results');
            
            let html = `
                <h6>Run: ${data.run_name}</h6>
                <p class="mb-3">${data.summary}</p>
                <div class="list-group">
            `;
            
            data.findings.forEach(finding => {
                const alertClass = finding.type === 'error' ? 'danger' : 
                                   finding.type === 'warning' ? 'warning' : 'info';
                html += `
                    <div class="list-group-item list-group-item-${alertClass}">
                        <strong>${finding.category}</strong>: ${finding.message}
                        <br><small>${finding.recommendation}</small>
                    </div>
                `;
            });
            
            html += '</div>';
            resultsDiv.innerHTML = html;
        })
        .catch(error => {
            console.error('Error running diagnostics:', error);
            alert('Error running diagnostics');
        });
}
