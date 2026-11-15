from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO, ProcessDAO, EventLogDAO
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
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Process name is required'}), 400

    burst_time = data.get('burst_time')
    if burst_time is None or int(burst_time) < 1:
        return jsonify({'error': 'burst_time must be at least 1'}), 400

    process = ProcessDAO.create(
        run_id=run_id,
        name=name,
        arrival_time=int(data.get('arrival_time', 0)),
        burst_time=int(burst_time),
        priority=int(data.get('priority', 0))
    )
    EventLogDAO.create(
        run_id, 'process', 'info',
        f"Process '{name}' added (arrival={process['arrival_time']}, burst={process['burst_time']})"
    )
    return jsonify(ProcessDAO.to_dict(process)), 201

@processes_bp.route('/processes/<int:process_id>', methods=['DELETE'])
def delete_process(process_id):
    process = ProcessDAO.get_by_id(process_id)
    if not process:
        return jsonify({'error': 'Process not found'}), 404
    ProcessDAO.delete(process_id)
    EventLogDAO.create(
        process['run_id'], 'process', 'warning',
        f"Process '{process['name']}' deleted"
    )
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

    EventLogDAO.create(
        run_id, 'process', 'info',
        f"Imported {len(imported)} processes from the running system"
    )
    return jsonify({
        'message': f'Imported {len(imported)} processes from system',
        'processes': [ProcessDAO.to_dict(p) for p in imported]
    }), 201
