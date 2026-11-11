from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO

runs_bp = Blueprint('runs', __name__)

@runs_bp.route('/runs', methods=['GET'])
def get_runs():
    runs = SimulationRunDAO.get_all()
    return jsonify([SimulationRunDAO.to_dict(r) for r in runs])

@runs_bp.route('/runs', methods=['POST'])
def create_run():
    data = request.get_json()
    run = SimulationRunDAO.create(
        name=data.get('name'),
        description=data.get('description')
    )
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
    run = SimulationRunDAO.finish(run_id)
    return jsonify(SimulationRunDAO.to_dict(run))
