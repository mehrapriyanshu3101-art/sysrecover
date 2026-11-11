from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO
from database.mysql_connection import db

events_bp = Blueprint('events', __name__)

@events_bp.route('/runs/<int:run_id>/events', methods=['GET'])
def get_events(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    
    severity = request.args.get('severity')
    event_type = request.args.get('event_type')
    
    query = "SELECT * FROM event_log WHERE run_id = %s"
    params = [run_id]
    
    if severity:
        query += " AND severity = %s"
        params.append(severity)
    if event_type:
        query += " AND event_type = %s"
        params.append(event_type)
    
    query += " ORDER BY timestamp DESC"
    
    events = db.execute_query(query, tuple(params))
    
    return jsonify(events)
