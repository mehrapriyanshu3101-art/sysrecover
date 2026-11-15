from database.mysql_connection import db

class EventLogDAO:
    """Data Access Object for EventLog table"""
    
    @staticmethod
    def get_by_run_id(run_id, limit=None):
        """Get all events for a simulation run"""
        query = "SELECT * FROM event_log WHERE run_id = %s ORDER BY timestamp DESC"
        if limit:
            query += f" LIMIT {limit}"
        return db.execute_query(query, (run_id,))
    
    @staticmethod
    def create(run_id, event_type, severity='info', details=None):
        """Create a new event log entry"""
        query = """
            INSERT INTO event_log (run_id, event_type, severity, details)
            VALUES (%s, %s, %s, %s)
        """
        event_id = db.execute_query(query, (run_id, event_type, severity, details), fetch=False)
        return event_id
    
    @staticmethod
    def to_dict(event):
        """Convert database row to dictionary"""
        return {
            'event_id': event['event_id'],
            'run_id': event['run_id'],
            'event_type': event['event_type'],
            'severity': event['severity'],
            'details': event['details'],
            'timestamp': event['timestamp']
        }
