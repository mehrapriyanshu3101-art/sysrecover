function initReports() {
    if (activeRunId) {
        loadReport();
    } else {
        document.getElementById('report-content').innerHTML = 
            '<p class="text-muted">Please select a simulation run to generate report</p>';
    }
}

function loadReport() {
    if (!activeRunId) {
        document.getElementById('report-content').innerHTML = 
            '<p class="text-muted">Please select a simulation run to generate report</p>';
        return;
    }
    
    fetch(`/api/runs/${activeRunId}/reports`)
        .then(response => response.json())
        .then(data => {
            displayReport(data);
        })
        .catch(error => {
            console.error('Error loading report:', error);
            document.getElementById('report-content').innerHTML = 
                '<p class="text-danger">Error loading report</p>';
        });
}

function displayReport(data) {
    const content = document.getElementById('report-content');
    content.innerHTML = `
        <h5>Simulation Report: ${data.run_name}</h5>
        <hr>
        <div class="row">
            <div class="col-md-6">
                <h6>Run Information</h6>
                <ul>
                    <li><strong>Run ID:</strong> ${data.run_id}</li>
                    <li><strong>Status:</strong> ${data.status}</li>
                </ul>
            </div>
            <div class="col-md-6">
                <h6>Summary</h6>
                <p>${data.summary}</p>
            </div>
        </div>
        
        <div class="mt-4">
            <button class="btn btn-primary" onclick="window.print()">
                <i class="bi bi-printer"></i> Print Report
            </button>
            <button class="btn btn-secondary" onclick="exportCSV()">
                <i class="bi bi-download"></i> Export CSV
            </button>
        </div>
    `;
}

function exportCSV() {
    alert('CSV export functionality to be implemented');
}
