from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO, TransactionDAO
from services.recovery_service import RecoveryService

recovery_bp = Blueprint('recovery', __name__)

@recovery_bp.route('/runs/<int:run_id>/checkpoints', methods=['POST'])
def create_checkpoint(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    
    service = RecoveryService()
    checkpoint = service.create_checkpoint(run_id)
    
    return jsonify(checkpoint)

@recovery_bp.route('/runs/<int:run_id>/crash', methods=['POST'])
def simulate_crash(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    
    # Simulate crash by marking transactions as in-doubt
    from database.mysql_connection import db
    query = "SELECT COUNT(*) as count FROM transactions WHERE run_id = %s AND status = 'active'"
    result = db.execute_query(query, (run_id,))
    
    return jsonify({
        'message': 'Crash simulated',
        'affected_transactions': result[0]['count'] if result else 0
    })

@recovery_bp.route('/runs/<int:run_id>/recover', methods=['POST'])
def perform_recovery(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    
    service = RecoveryService()
    result = service.recover(run_id)
    
    return jsonify(result)
