let ganttChart = null;

function initScheduling() {
    initializeSchedulingForm();
}

function initializeSchedulingForm() {
    const algorithmSelect = document.getElementById('scheduling-algorithm');
    const timeQuantumGroup = document.getElementById('time-quantum-group');
    
    algorithmSelect.addEventListener('change', function() {
        timeQuantumGroup.style.display = this.value === 'round_robin' ? 'block' : 'none';
    });
    
    const form = document.getElementById('scheduling-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!activeRunId) {
            alert('Please select a simulation run first');
            return;
        }
        
        const algorithm = document.getElementById('scheduling-algorithm').value;
        const timeQuantum = parseInt(document.getElementById('time-quantum').value);
        
        fetch(`/api/runs/${activeRunId}/scheduling/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ algorithm, time_quantum: timeQuantum })
        })
        .then(response => response.json())
        .then(data => {
            displaySchedulingResults(data);
        })
        .catch(error => {
            console.error('Error running scheduling:', error);
            alert('Error running scheduling');
        });
    });
}

function displaySchedulingResults(data) {
    // Display metrics
    const metricsDiv = document.getElementById('scheduling-metrics');
    const avgTurnaround = data.processes.reduce((sum, p) => sum + (p.turnaround_time || 0), 0) / data.processes.length;
    const avgWaiting = data.processes.reduce((sum, p) => sum + (p.waiting_time || 0), 0) / data.processes.length;
    
    metricsDiv.innerHTML = `
        <p><strong>Algorithm:</strong> ${data.algorithm}</p>
        <p><strong>Average Turnaround Time:</strong> ${avgTurnaround.toFixed(2)}</p>
        <p><strong>Average Waiting Time:</strong> ${avgWaiting.toFixed(2)}</p>
    `;
    
    // Display results table
    const resultsTable = document.getElementById('scheduling-results');
    resultsTable.innerHTML = data.processes.map(p => `
        <tr>
            <td>${p.name}</td>
            <td>${p.arrival_time}</td>
            <td>${p.burst_time}</td>
            <td>${p.completion_time}</td>
            <td>${p.turnaround_time}</td>
            <td>${p.waiting_time}</td>
        </tr>
    `).join('');
    
    // Display Gantt chart
    displayGanttChart(data.gantt_chart);
}

function displayGanttChart(ganttData) {
    const ctx = document.getElementById('ganttChart');
    if (!ctx) return;
    
    if (ganttChart) {
        ganttChart.destroy();
    }
    
    const labels = ganttData.map(g => g.process);
    const data = ganttData.map(g => g.duration);
    
    ganttChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Execution Time',
                data: data,
                backgroundColor: '#0d6efd'
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            }
        }
    });
}
