from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO, TransactionDAO, EventLogDAO
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
    data = request.get_json() or {}
    trans_type = data.get('type', 'general')
    process_id = data.get('process_id')

    transaction = TransactionDAO.create(
        run_id=run_id,
        trans_type=trans_type,
        process_id=process_id
    )
    EventLogDAO.create(
        run_id, 'transaction', 'info',
        f"Transaction {transaction['transaction_id']} started ({trans_type})"
    )
    return jsonify(TransactionDAO.to_dict(transaction)), 201

@transactions_bp.route('/data-store', methods=['GET'])
def get_data_store():
    return jsonify(TransactionService.data_store)

@transactions_bp.route('/transactions/<int:transaction_id>/operations', methods=['POST'])
def execute_operation(transaction_id):
    transaction = TransactionDAO.get_by_id(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    if transaction['status'] != 'active':
        return jsonify({'error': f"Transaction is {transaction['status']}, not active"}), 400

    data = request.get_json() or {}
    operation = data.get('operation')
    data_item = data.get('data_item')

    if data_item not in TransactionService.data_store:
        return jsonify({'error': 'data_item must be A or B'}), 400

    service = TransactionService()

    if operation == 'read':
        return jsonify(service.read(transaction_id, data_item))

    if operation == 'write':
        new_value = data.get('new_value')
        if new_value is None or new_value == '':
            return jsonify({'error': 'new_value is required for a write'}), 400
        result = service.write(transaction_id, transaction['run_id'], data_item, int(new_value))
        EventLogDAO.create(
            transaction['run_id'], 'transaction', 'info',
            f"Transaction {transaction_id} wrote {data_item} = {new_value}"
        )
        return jsonify(result)

    return jsonify({'error': "operation must be 'read' or 'write'"}), 400

@transactions_bp.route('/transactions/<int:transaction_id>/commit', methods=['POST'])
def commit_transaction(transaction_id):
    transaction = TransactionDAO.get_by_id(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    if transaction['status'] != 'active':
        return jsonify({'error': f"Transaction is already {transaction['status']}"}), 400

    service = TransactionService()
    result = service.commit(transaction_id)
    EventLogDAO.create(
        transaction['run_id'], 'transaction', 'info',
        f"Transaction {transaction_id} committed"
    )
    return jsonify(result)

@transactions_bp.route('/transactions/<int:transaction_id>/rollback', methods=['POST'])
def rollback_transaction(transaction_id):
    transaction = TransactionDAO.get_by_id(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    if transaction['status'] != 'active':
        return jsonify({'error': f"Transaction is already {transaction['status']}"}), 400

    service = TransactionService()
    result = service.rollback(transaction_id)
    EventLogDAO.create(
        transaction['run_id'], 'transaction', 'warning',
        f"Transaction {transaction_id} rolled back"
    )
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

    EventLogDAO.create(
        run_id, 'transaction', 'info',
        f"Generated {len(created)} transactions automatically"
    )
    return jsonify({
        'message': f'Generated {len(created)} transactions',
        'transactions': [TransactionDAO.to_dict(t) for t in created]
    }), 201
