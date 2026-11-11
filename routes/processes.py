from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO, ProcessDAO
from services.system_process_service import SystemProcessService

processes_bp = Blueprint('processes', __name__)

@processes_bp.route('/runs/<int:run_id>/processes', methods=['GET'])
def get_processes(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    processes = ProcessDAO.get_by_run_id(run_id)
    return jsonify([ProcessDAO.to_dict(p) for p in processes])

@processes_bp.route('/runs/<int:run_id>/processes', methods=['POST'])
def create_process(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    data = request.get_json()
    
    process = ProcessDAO.create(
        run_id=run_id,
        name=data.get('name'),
        arrival_time=data.get('arrival_time', 0),
        burst_time=data.get('burst_time'),
        priority=data.get('priority', 0)
    )
    return jsonify(ProcessDAO.to_dict(process)), 201

@processes_bp.route('/processes/<int:process_id>', methods=['DELETE'])
def delete_process(process_id):
    if not ProcessDAO.get_by_id(process_id):
        return jsonify({'error': 'Process not found'}), 404
    ProcessDAO.delete(process_id)
    return jsonify({'message': 'Process deleted'})

@processes_bp.route('/runs/<int:run_id>/processes/auto-import', methods=['POST'])
def auto_import_processes(run_id):
    """Automatically import processes from Windows Task Manager"""
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    
    service = SystemProcessService()
    system_processes = service.get_system_processes(limit=15)
    
    imported = []
    for proc_data in system_processes:
        process = ProcessDAO.create(
            run_id=run_id,
            name=proc_data['name'],
            arrival_time=proc_data['arrival_time'],
            burst_time=proc_data['burst_time'],
            priority=proc_data['priority']
        )
        imported.append(process)
    
    return jsonify({
        'message': f'Imported {len(imported)} processes from system',
        'processes': [ProcessDAO.to_dict(p) for p in imported]
    }), 201
