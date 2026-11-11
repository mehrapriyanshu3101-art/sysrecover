from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO
from services.memory_service import MemoryService
from services.system_memory_service import SystemMemoryService

memory_bp = Blueprint('memory', __name__)

@memory_bp.route('/runs/<int:run_id>/memory/run', methods=['POST'])
def run_memory_simulation(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    data = request.get_json()
    
    reference_string = data.get('reference_string', [])
    num_frames = data.get('num_frames', 3)
    algorithm = data.get('algorithm', 'fifo')
    
    service = MemoryService()
    result = service.run_simulation(reference_string, num_frames, algorithm)
    
    return jsonify(result)

@memory_bp.route('/runs/<int:run_id>/memory/auto-import', methods=['POST'])
def auto_import_memory(run_id):
    """Automatically generate memory reference string from system patterns"""
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    
    service = SystemMemoryService()
    reference_string = service.get_memory_reference_string(length=20)
    memory_info = service.get_system_memory_info()
    
    return jsonify({
        'reference_string': reference_string,
        'num_frames': memory_info['recommended_frames'],
        'system_info': memory_info,
        'message': 'Generated reference string from system memory patterns'
    })
