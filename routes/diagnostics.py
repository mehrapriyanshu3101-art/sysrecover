from flask import Blueprint, jsonify
from database.dao import SimulationRunDAO
from services.diagnostic_service import DiagnosticService

diagnostics_bp = Blueprint('diagnostics', __name__)

@diagnostics_bp.route('/runs/<int:run_id>/diagnostics', methods=['GET'])
def run_diagnostics(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    
    service = DiagnosticService()
    result = service.analyze(run_id)
    
    return jsonify(result)
