from datetime import datetime
from database.connection import db

class Transaction(db.Model):
    __tablename__ = 'transaction'
    
    transaction_id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('simulation_run.run_id'), nullable=False)
    process_id = db.Column(db.Integer, db.ForeignKey('process.process_id'), nullable=True)
    type = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')  # active, waiting, committed, aborted
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    commit_time = db.Column(db.DateTime)
    rollback_time = db.Column(db.DateTime)
    two_phase_state = db.Column(db.String(20), default='growing')  # growing, shrinking
    
    # Relationships
    locks = db.relationship('Lock', backref='transaction', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'run_id': self.run_id,
            'process_id': self.process_id,
            'type': self.type,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'commit_time': self.commit_time.isoformat() if self.commit_time else None,
            'rollback_time': self.rollback_time.isoformat() if self.rollback_time else None,
            'two_phase_state': self.two_phase_state
        }
