from models import SimulationRun, Process, Transaction, EventLog

class DiagnosticService:
    def analyze(self, run_id):
        """Analyze simulation run and generate findings"""
        run = SimulationRun.query.get(run_id)
        processes = Process.query.filter_by(run_id=run_id).all()
        transactions = Transaction.query.filter_by(run_id=run_id).all()
        events = EventLog.query.filter_by(run_id=run_id).all()
        
        findings = []
        
        # Analyze processes
        if processes:
            avg_waiting = sum(p.waiting_time or 0 for p in processes) / len(processes)
            if avg_waiting > 10:
                findings.append({
                    'type': 'warning',
                    'category': 'Process Scheduling',
                    'message': f'High average waiting time: {avg_waiting:.2f}',
                    'recommendation': 'Consider using Round Robin or Priority scheduling'
                })
        
        # Analyze transactions
        active_transactions = [t for t in transactions if t.status == 'active']
        if len(active_transactions) > 5:
            findings.append({
                'type': 'warning',
                'category': 'Concurrency',
                'message': f'Many active transactions: {len(active_transactions)}',
                'recommendation': 'Consider committing some transactions to reduce lock contention'
            })
        
        # Analyze events
        error_events = [e for e in events if e.severity == 'error']
        if error_events:
            findings.append({
                'type': 'error',
                'category': 'System Health',
                'message': f'{len(error_events)} error events detected',
                'recommendation': 'Review error logs for system issues'
            })
        
        if not findings:
            findings.append({
                'type': 'info',
                'category': 'System Health',
                'message': 'No issues detected',
                'recommendation': 'System is running optimally'
            })
        
        return {
            'run_id': run_id,
            'run_name': run.name,
            'findings': findings,
            'summary': f'{len(findings)} findings detected'
        }
