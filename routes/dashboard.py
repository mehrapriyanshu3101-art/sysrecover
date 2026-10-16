from flask import Blueprint, jsonify
from models import SimulationRun, Process, Transaction, EventLog
from database.connection import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/runs/<int:run_id>/dashboard', methods=['GET'])
def get_dashboard_metrics(run_id):
    SimulationRun.query.get_or_404(run_id)
    
    process_count = Process.query.filter_by(run_id=run_id).count()
    transaction_count = Transaction.query.filter_by(run_id=run_id).count()
    recent_events = EventLog.query.filter_by(run_id=run_id).order_by(EventLog.timestamp.desc()).limit(10).all()
    
    run = SimulationRun.query.get(run_id)
    
    return jsonify({
        'process_count': process_count,
        'transaction_count': transaction_count,
        'status': run.status,
        'recent_events': [e.to_dict() for e in recent_events]
    })
