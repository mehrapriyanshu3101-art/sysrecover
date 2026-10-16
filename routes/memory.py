from flask import Blueprint, request, jsonify
from models import SimulationRun
from services.memory_service import MemoryService

memory_bp = Blueprint('memory', __name__)

@memory_bp.route('/runs/<int:run_id>/memory/run', methods=['POST'])
def run_memory_simulation(run_id):
    SimulationRun.query.get_or_404(run_id)
    data = request.get_json()
    
    reference_string = data.get('reference_string', [])
    num_frames = data.get('num_frames', 3)
    algorithm = data.get('algorithm', 'fifo')
    
    service = MemoryService()
    result = service.run_simulation(reference_string, num_frames, algorithm)
    
    return jsonify(result)
