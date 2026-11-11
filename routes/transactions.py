from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO, TransactionDAO
from services.transaction_service import TransactionService
from services.system_transaction_service import SystemTransactionService

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/runs/<int:run_id>/transactions', methods=['GET'])
def get_transactions(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    transactions = TransactionDAO.get_by_run_id(run_id)
    return jsonify([TransactionDAO.to_dict(t) for t in transactions])

@transactions_bp.route('/runs/<int:run_id>/transactions', methods=['POST'])
def create_transaction(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    data = request.get_json()
    trans_type = data.get('type', 'general')
    process_id = data.get('process_id')
    
    transaction = TransactionDAO.create(
        run_id=run_id,
        trans_type=trans_type,
        process_id=process_id
    )
    return jsonify(TransactionDAO.to_dict(transaction)), 201

@transactions_bp.route('/transactions/<int:transaction_id>/commit', methods=['POST'])
def commit_transaction(transaction_id):
    if not TransactionDAO.get_by_id(transaction_id):
        return jsonify({'error': 'Transaction not found'}), 404
    service = TransactionService()
    result = service.commit(transaction_id)
    return jsonify(result)

@transactions_bp.route('/transactions/<int:transaction_id>/rollback', methods=['POST'])
def rollback_transaction(transaction_id):
    if not TransactionDAO.get_by_id(transaction_id):
        return jsonify({'error': 'Transaction not found'}), 404
    service = TransactionService()
    result = service.rollback(transaction_id)
    return jsonify(result)

@transactions_bp.route('/runs/<int:run_id>/transactions/auto-generate', methods=['POST'])
def auto_generate_transactions(run_id):
    """Automatically generate realistic transactions"""
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    
    service = SystemTransactionService()
    transaction_data = service.generate_transactions(count=5)
    
    created = []
    for trans_data in transaction_data:
        transaction = TransactionDAO.create(
            run_id=run_id,
            trans_type=trans_data['type'],
            process_id=trans_data['process_id']
        )
        created.append(transaction)
    
    return jsonify({
        'message': f'Generated {len(created)} transactions',
        'transactions': [TransactionDAO.to_dict(t) for t in created]
    }), 201
