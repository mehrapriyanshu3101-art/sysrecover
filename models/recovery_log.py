from datetime import datetime
from database.connection import db

class RecoveryLog(db.Model):
    __tablename__ = 'recovery_log'
    
    log_id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('simulation_run.run_id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'), nullable=False)
    lsn = db.Column(db.Integer, nullable=False)  # Log Sequence Number
    operation = db.Column(db.String(20), nullable=False)  # read, write, commit, abort
    data_item = db.Column(db.String(50))
    old_value = db.Column(db.String(100))
    new_value = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'run_id': self.run_id,
            'transaction_id': self.transaction_id,
            'lsn': self.lsn,
            'operation': self.operation,
            'data_item': self.data_item,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
