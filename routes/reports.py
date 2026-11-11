from flask import Blueprint, jsonify
from database.dao import SimulationRunDAO

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/runs/<int:run_id>/reports', methods=['GET'])
def get_report(run_id):
    run = SimulationRunDAO.get_by_id(run_id)
    if not run:
        return jsonify({'error': 'Run not found'}), 404
    
    return jsonify({
        'run_id': run['run_id'],
        'run_name': run['name'],
        'status': run['status'],
        'summary': f'Simulation run {run["name"]} with status {run["status"]}'
    })
