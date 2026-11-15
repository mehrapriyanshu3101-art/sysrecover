function initDeadlocks() {
    if (activeRunId) {
        detectDeadlock();
    }
}

function detectDeadlock() {
    if (!activeRunId) {
        const statusDiv = document.getElementById('deadlock-status');
        statusDiv.innerHTML = '<div class="alert alert-info">Please select a simulation run first</div>';
        return;
    }

    fetch(`/api/runs/${activeRunId}/deadlocks/detect`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        const statusDiv = document.getElementById('deadlock-status');
        const graphDiv = document.getElementById('wait-for-graph');
        const infoDiv = document.getElementById('deadlock-info');

        if (data.deadlock_detected) {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Deadlock Detected!</strong><br>
                    <small>${data.message}</small>
                </div>
            `;
            // Draw graph visualization
            graphDiv.innerHTML = `
                <canvas id="deadlockGraph" width="600" height="300"></canvas>
            `;
            infoDiv.innerHTML = `
                <h6>Wait-For Graph Structure</h6>
                <pre>${JSON.stringify(data.graph, null, 2)}</pre>
            `;
            drawWaitForGraph(data.graph);
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <strong>No Deadlock</strong>
                </div>
            `;
            graphDiv.innerHTML = '<p class="text-muted">No deadlock detected in the system</p>';
            infoDiv.innerHTML = '<p class="text-muted">No deadlock information available</p>';
        }
    })
    .catch(error => {
        console.error('Error detecting deadlock:', error);
        alert('Error detecting deadlock');
    });
}

// Abort a transaction from the detected cycle and re-check the graph
function recoverDeadlock() {
    if (!activeRunId) {
        alert('Please select a simulation run first');
        return;
    }

    fetch(`/api/runs/${activeRunId}/deadlocks/detect`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (!data.deadlock_detected) {
            alert('No deadlock to recover from');
            return;
        }

        const victim = parseInt(data.transactions[0]);

        if (!confirm(`This will abort transaction T${victim} to break the deadlock. Continue?`)) {
            return;
        }

        return fetch(`/api/runs/${activeRunId}/deadlocks/recover`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ victim_transaction_id: victim })
        })
        .then(response => response.json().then(body => ({ ok: response.ok, body })))
        .then(({ ok, body }) => {
            if (!ok) {
                alert(body.error || 'Error recovering deadlock');
                return;
            }

            const statusDiv = document.getElementById('deadlock-status');
            statusDiv.innerHTML = `
                <div class="alert alert-warning">
                    <strong>Deadlock Resolved</strong><br>
                    Transaction T${body.victim_transaction_id} aborted, ${body.locks_released} lock(s) released
                </div>
            `;
            detectDeadlock();
        });
    })
    .catch(error => {
        console.error('Error recovering deadlock:', error);
        alert('Error recovering deadlock');
    });
}

function drawWaitForGraph(graph) {
    const canvas = document.getElementById('deadlockGraph');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const nodes = Object.keys(graph);

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Position nodes in a circle
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 100;

    const nodePositions = {};
    nodes.forEach((node, index) => {
        const angle = (2 * Math.PI * index) / nodes.length;
        nodePositions[node] = {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle)
        };
    });

    // Draw edges
    ctx.strokeStyle = '#dc3545';
    ctx.lineWidth = 2;
    Object.keys(graph).forEach(fromNode => {
        graph[fromNode].forEach(toNode => {
            const from = nodePositions[fromNode];
            const to = nodePositions[toNode];
            if (!from || !to) return;

            ctx.beginPath();
            ctx.moveTo(from.x, from.y);
            ctx.lineTo(to.x, to.y);
            ctx.stroke();

            // Draw arrow
            const angle = Math.atan2(to.y - from.y, to.x - from.x);
            const arrowLength = 10;
            ctx.beginPath();
            ctx.moveTo(to.x, to.y);
            ctx.lineTo(to.x - arrowLength * Math.cos(angle - Math.PI / 6), to.y - arrowLength * Math.sin(angle - Math.PI / 6));
            ctx.moveTo(to.x, to.y);
            ctx.lineTo(to.x - arrowLength * Math.cos(angle + Math.PI / 6), to.y - arrowLength * Math.sin(angle + Math.PI / 6));
            ctx.stroke();
        });
    });

    // Draw nodes
    nodes.forEach(node => {
        const pos = nodePositions[node];

        // Draw circle
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 25, 0, 2 * Math.PI);
        ctx.fillStyle = '#007bff';
        ctx.fill();
        ctx.strokeStyle = '#0056b3';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Draw label
        ctx.fillStyle = '#ffffff';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`T${node}`, pos.x, pos.y);
    });
}
