from flask import Blueprint, jsonify
from models import SimulationRun
from services.diagnostic_service import DiagnosticService

diagnostics_bp = Blueprint('diagnostics', __name__)

@diagnostics_bp.route('/runs/<int:run_id>/diagnostics', methods=['GET'])
def run_diagnostics(run_id):
    SimulationRun.query.get_or_404(run_id)
    
    service = DiagnosticService()
    result = service.analyze(run_id)
    
    return jsonify(result)
