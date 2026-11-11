from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO, TransactionDAO, LockDAO
from services.deadlock_service import DeadlockService

deadlocks_bp = Blueprint('deadlocks', __name__)

@deadlocks_bp.route('/runs/<int:run_id>/deadlocks/detect', methods=['POST'])
def detect_deadlocks(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    
    locks = LockDAO.get_waiting_locks()
    service = DeadlockService()
    
    result = service.detect_deadlock(locks)
    
    return jsonify(result)

@deadlocks_bp.route('/runs/<int:run_id>/deadlocks/recover', methods=['POST'])
def recover_deadlock(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    data = request.get_json()
    
    victim_id = data.get('victim_transaction_id')
    transaction = TransactionDAO.get_by_id(victim_id)
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    # Update transaction status to aborted
    from database.mysql_connection import db
    query = "UPDATE transaction SET status = 'aborted' WHERE transaction_id = %s"
    db.execute_query(query, (victim_id,), fetch=False)
    
    return jsonify({'message': f'Transaction {victim_id} aborted to resolve deadlock'})
