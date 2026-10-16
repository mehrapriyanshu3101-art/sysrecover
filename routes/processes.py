from flask import Blueprint, request, jsonify
from models import SimulationRun, Process
from database.connection import db

processes_bp = Blueprint('processes', __name__)

@processes_bp.route('/runs/<int:run_id>/processes', methods=['GET'])
def get_processes(run_id):
    SimulationRun.query.get_or_404(run_id)
    processes = Process.query.filter_by(run_id=run_id).all()
    return jsonify([p.to_dict() for p in processes])

@processes_bp.route('/runs/<int:run_id>/processes', methods=['POST'])
def create_process(run_id):
    SimulationRun.query.get_or_404(run_id)
    data = request.get_json()
    
    process = Process(
        run_id=run_id,
        name=data.get('name'),
        arrival_time=data.get('arrival_time', 0),
        burst_time=data.get('burst_time'),
        priority=data.get('priority', 0)
    )
    db.session.add(process)
    db.session.commit()
    return jsonify(process.to_dict()), 201

@processes_bp.route('/processes/<int:process_id>', methods=['DELETE'])
def delete_process(process_id):
    process = Process.query.get_or_404(process_id)
    db.session.delete(process)
    db.session.commit()
    return jsonify({'message': 'Process deleted'})
