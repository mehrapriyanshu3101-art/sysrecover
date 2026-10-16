from flask import Blueprint, request
from models import SimulationRun, EventLog

events_bp = Blueprint('events', __name__)

@events_bp.route('/runs/<int:run_id>/events', methods=['GET'])
def get_events(run_id):
    SimulationRun.query.get_or_404(run_id)
    
    severity = request.args.get('severity')
    event_type = request.args.get('event_type')
    
    query = EventLog.query.filter_by(run_id=run_id)
    
    if severity:
        query = query.filter_by(severity=severity)
    if event_type:
        query = query.filter_by(event_type=event_type)
    
    events = query.order_by(EventLog.timestamp.desc()).all()
    
    return jsonify([e.to_dict() for e in events])
