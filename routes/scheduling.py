from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO, ProcessDAO, EventLogDAO
from services.scheduling_service import SchedulingService

scheduling_bp = Blueprint('scheduling', __name__)

@scheduling_bp.route('/runs/<int:run_id>/scheduling/run', methods=['POST'])
def run_scheduling(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    data = request.get_json() or {}

    algorithm = data.get('algorithm', 'fcfs')
    time_quantum = data.get('time_quantum', 2)

    try:
        time_quantum = max(1, int(time_quantum))
    except (TypeError, ValueError):
        time_quantum = 2

    processes = ProcessDAO.get_by_run_id(run_id)

    if not processes:
        return jsonify({'error': 'No processes in this run. Add processes first.'}), 400

    # Convert to process-like objects for the service
    class ProcessObj:
        def __init__(self, row):
            self.process_id = row['process_id']
            self.name = row['name']
            self.arrival_time = row['arrival_time']
            self.burst_time = row['burst_time']
            self.priority = row['priority']
            self.completion_time = None
            self.turnaround_time = None
            self.waiting_time = None

        def to_dict(self):
            return {
                'process_id': self.process_id,
                'name': self.name,
                'arrival_time': self.arrival_time,
                'burst_time': self.burst_time,
                'priority': self.priority,
                'completion_time': self.completion_time,
                'turnaround_time': self.turnaround_time,
                'waiting_time': self.waiting_time
            }

    process_objs = [ProcessObj(p) for p in processes]
    service = SchedulingService()

    result = service.run_algorithm(algorithm, process_objs, time_quantum)

    # Update process metrics
    for p in process_objs:
        ProcessDAO.update_metrics(
            p.process_id,
            p.completion_time,
            p.turnaround_time,
            p.waiting_time
        )

    EventLogDAO.create(
        run_id, 'process', 'info',
        f"{result['algorithm']} scheduling executed on {len(process_objs)} process(es)"
    )

    return jsonify(result)
