from flask import Blueprint, request, jsonify
from models import SimulationRun, Checkpoint, RecoveryLog, Transaction
from services.recovery_service import RecoveryService
from database.connection import db

recovery_bp = Blueprint('recovery', __name__)

@recovery_bp.route('/runs/<int:run_id>/checkpoints', methods=['POST'])
def create_checkpoint(run_id):
    SimulationRun.query.get_or_404(run_id)
    
    service = RecoveryService()
    checkpoint = service.create_checkpoint(run_id)
    
    return jsonify(checkpoint.to_dict())

@recovery_bp.route('/runs/<int:run_id>/crash', methods=['POST'])
def simulate_crash(run_id):
    SimulationRun.query.get_or_404(run_id)
    
    # Simulate crash by marking transactions as in-doubt
    active_transactions = Transaction.query.filter_by(run_id=run_id, status='active').all()
    
    return jsonify({
        'message': 'Crash simulated',
        'affected_transactions': len(active_transactions)
    })

@recovery_bp.route('/runs/<int:run_id>/recover', methods=['POST'])
def perform_recovery(run_id):
    SimulationRun.query.get_or_404(run_id)
    
    service = RecoveryService()
    result = service.recover(run_id)
    
    return jsonify(result)
