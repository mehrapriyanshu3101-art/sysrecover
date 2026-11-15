from flask import Blueprint, jsonify
from database.dao import SimulationRunDAO, TransactionDAO, CheckpointDAO, RecoveryLogDAO, EventLogDAO
from database.mysql_connection import db
from services.recovery_service import RecoveryService

recovery_bp = Blueprint('recovery', __name__)

@recovery_bp.route('/runs/<int:run_id>/checkpoints', methods=['GET'])
def get_checkpoints(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    checkpoints = CheckpointDAO.get_by_run_id(run_id)
    return jsonify([CheckpointDAO.to_dict(c) for c in checkpoints])

@recovery_bp.route('/runs/<int:run_id>/checkpoints', methods=['POST'])
def create_checkpoint(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404

    service = RecoveryService()
    checkpoint = service.create_checkpoint(run_id)

    EventLogDAO.create(
        run_id, 'recovery', 'info',
        f"Checkpoint created at LSN {checkpoint['lsn']} "
        f"with {len(checkpoint['active_transactions'])} active transaction(s)"
    )
    return jsonify(checkpoint)

@recovery_bp.route('/runs/<int:run_id>/recovery-logs', methods=['GET'])
def get_recovery_logs(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    logs = RecoveryLogDAO.get_by_run_id(run_id)
    return jsonify([RecoveryLogDAO.to_dict(log) for log in logs])

@recovery_bp.route('/runs/<int:run_id>/crash', methods=['POST'])
def simulate_crash(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404

    # Count the transactions that were still active when the crash happened
    query = "SELECT COUNT(*) as count FROM transactions WHERE run_id = %s AND status = 'active'"
    result = db.execute_query(query, (run_id,))
    affected = result[0]['count'] if result else 0

    EventLogDAO.create(
        run_id, 'recovery', 'critical',
        f"System crash simulated: {affected} in-doubt transaction(s)"
    )

    return jsonify({
        'message': 'Crash simulated',
        'affected_transactions': affected
    })

@recovery_bp.route('/runs/<int:run_id>/recover', methods=['POST'])
def perform_recovery(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404

    service = RecoveryService()
    result = service.recover(run_id)

    EventLogDAO.create(
        run_id, 'recovery', 'info',
        result.get('message', 'Recovery completed')
    )
    return jsonify(result)
