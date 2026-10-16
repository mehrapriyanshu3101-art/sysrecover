from datetime import datetime
from database.connection import db

class Checkpoint(db.Model):
    __tablename__ = 'checkpoint'
    
    checkpoint_id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('simulation_run.run_id'), nullable=False)
    lsn = db.Column(db.Integer, nullable=False)  # LSN at checkpoint
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    active_transactions = db.Column(db.Text)  # JSON string of active transaction IDs
    
    def to_dict(self):
        return {
            'checkpoint_id': self.checkpoint_id,
            'run_id': self.run_id,
            'lsn': self.lsn,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'active_transactions': self.active_transactions
        }
