from flask import Blueprint, jsonify
from database.dao import SimulationRunDAO, ProcessDAO, TransactionDAO
from database.mysql_connection import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/runs/<int:run_id>/dashboard', methods=['GET'])
def get_dashboard_metrics(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    
    processes = ProcessDAO.get_by_run_id(run_id)
    transactions = TransactionDAO.get_by_run_id(run_id)
    
    query = "SELECT * FROM event_log WHERE run_id = %s ORDER BY timestamp DESC LIMIT 10"
    recent_events = db.execute_query(query, (run_id,))
    
    run = SimulationRunDAO.get_by_id(run_id)
    
    return jsonify({
        'process_count': len(processes),
        'transaction_count': len(transactions),
        'status': run['status'],
        'recent_events': recent_events
    })
