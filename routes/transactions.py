from flask import Blueprint, request, jsonify
from models import Transaction, SimulationRun
from database.connection import db
from services.transaction_service import TransactionService

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/runs/<int:run_id>/transactions', methods=['GET'])
def get_transactions(run_id):
    SimulationRun.query.get_or_404(run_id)
    transactions = Transaction.query.filter_by(run_id=run_id).all()
    return jsonify([t.to_dict() for t in transactions])

@transactions_bp.route('/runs/<int:run_id>/transactions', methods=['POST'])
def create_transaction(run_id):
    SimulationRun.query.get_or_404(run_id)
    data = request.get_json()
    
    trans_type = data.get('type', 'general')
    process_id = data.get('process_id')
    
    transaction = Transaction(
        run_id=run_id,
        type=trans_type,
        process_id=process_id,
        status='active'
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify(transaction.to_dict()), 201

@transactions_bp.route('/transactions/<int:transaction_id>/commit', methods=['POST'])
def commit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    service = TransactionService()
    result = service.commit(transaction)
    return jsonify(result)

@transactions_bp.route('/transactions/<int:transaction_id>/rollback', methods=['POST'])
def rollback_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    service = TransactionService()
    result = service.rollback(transaction)
    return jsonify(result)
