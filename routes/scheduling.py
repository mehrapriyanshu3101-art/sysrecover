from flask import Blueprint, request, jsonify
from models import SimulationRun, Process
from services.scheduling_service import SchedulingService
from database.connection import db

scheduling_bp = Blueprint('scheduling', __name__)

@scheduling_bp.route('/runs/<int:run_id>/scheduling/run', methods=['POST'])
def run_scheduling(run_id):
    SimulationRun.query.get_or_404(run_id)
    data = request.get_json()
    
    algorithm = data.get('algorithm', 'fcfs')
    time_quantum = data.get('time_quantum', 2)
    
    processes = Process.query.filter_by(run_id=run_id).all()
    service = SchedulingService()
    
    result = service.run_algorithm(algorithm, processes, time_quantum)
    
    # Update process metrics
    for p in processes:
        db_process = Process.query.get(p.process_id)
        if db_process:
            db_process.completion_time = p.completion_time
            db_process.turnaround_time = p.turnaround_time
            db_process.waiting_time = p.waiting_time
            db_process.state = 'completed'
    
    db.session.commit()
    
    return jsonify(result)
