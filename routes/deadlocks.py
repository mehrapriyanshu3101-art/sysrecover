from flask import Blueprint, request, jsonify
from models import SimulationRun, Transaction, Lock
from services.deadlock_service import DeadlockService
from database.connection import db

deadlocks_bp = Blueprint('deadlocks', __name__)

@deadlocks_bp.route('/runs/<int:run_id>/deadlocks/detect', methods=['POST'])
def detect_deadlocks(run_id):
    SimulationRun.query.get_or_404(run_id)
    
    locks = Lock.query.filter_by(status='waiting').all()
    service = DeadlockService()
    
    result = service.detect_deadlock(locks)
    
    return jsonify(result)

@deadlocks_bp.route('/runs/<int:run_id>/deadlocks/recover', methods=['POST'])
def recover_deadlock(run_id):
    SimulationRun.query.get_or_404(run_id)
    data = request.get_json()
    
    victim_id = data.get('victim_transaction_id')
    transaction = Transaction.query.get_or_404(victim_id)
    
    transaction.status = 'aborted'
    db.session.commit()
    
    return jsonify({'message': f'Transaction {victim_id} aborted to resolve deadlock'})
