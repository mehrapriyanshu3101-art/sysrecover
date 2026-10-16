from flask import Blueprint, jsonify
from models import SimulationRun

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/runs/<int:run_id>/reports', methods=['GET'])
def get_report(run_id):
    run = SimulationRun.query.get_or_404(run_id)
    
    return jsonify({
        'run_id': run.run_id,
        'run_name': run.name,
        'status': run.status,
        'summary': f'Simulation run {run.name} with status {run.status}'
    })
