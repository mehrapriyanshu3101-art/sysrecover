from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO, EventLogDAO

runs_bp = Blueprint('runs', __name__)

@runs_bp.route('/runs', methods=['GET'])
def get_runs():
    runs = SimulationRunDAO.get_all()
    return jsonify([SimulationRunDAO.to_dict(r) for r in runs])

@runs_bp.route('/runs', methods=['POST'])
def create_run():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()

    if not name:
        return jsonify({'error': 'Run name is required'}), 400

    run = SimulationRunDAO.create(
        name=name,
        description=data.get('description')
    )
    EventLogDAO.create(run['run_id'], 'system', 'info', f"Simulation run '{name}' created")
    return jsonify(SimulationRunDAO.to_dict(run)), 201

@runs_bp.route('/runs/<int:run_id>', methods=['GET'])
def get_run(run_id):
    run = SimulationRunDAO.get_by_id(run_id)
    if not run:
        return jsonify({'error': 'Run not found'}), 404
    return jsonify(SimulationRunDAO.to_dict(run))

@runs_bp.route('/runs/<int:run_id>', methods=['DELETE'])
def delete_run(run_id):
    run = SimulationRunDAO.get_by_id(run_id)
    if not run:
        return jsonify({'error': 'Run not found'}), 404
    SimulationRunDAO.delete(run_id)
    return jsonify({'message': 'Run deleted'})

@runs_bp.route('/runs/<int:run_id>/finish', methods=['POST'])
def finish_run(run_id):
    run = SimulationRunDAO.get_by_id(run_id)
    if not run:
        return jsonify({'error': 'Run not found'}), 404
    if run['status'] == 'finished':
        return jsonify({'error': 'Run is already finished'}), 400

    run = SimulationRunDAO.finish(run_id)
    EventLogDAO.create(run_id, 'system', 'info', f"Simulation run '{run['name']}' finished")
    return jsonify(SimulationRunDAO.to_dict(run))
