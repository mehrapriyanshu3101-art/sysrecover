from datetime import datetime
from database.connection import db

class EventLog(db.Model):
    __tablename__ = 'event_log'
    
    event_id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('simulation_run.run_id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), default='info')  # info, warning, error, critical
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'event_id': self.event_id,
            'run_id': self.run_id,
            'event_type': self.event_type,
            'severity': self.severity,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
