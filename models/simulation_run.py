from datetime import datetime
from database.connection import db

class SimulationRun(db.Model):
    __tablename__ = 'simulation_run'
    
    run_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, finished
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)
    
    # Relationships
    processes = db.relationship('Process', backref='run', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='run', lazy=True, cascade='all, delete-orphan')
    resources = db.relationship('Resource', backref='run', lazy=True, cascade='all, delete-orphan')
    memory_pages = db.relationship('MemoryPage', backref='run', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('EventLog', backref='run', lazy=True, cascade='all, delete-orphan')
    recovery_logs = db.relationship('RecoveryLog', backref='run', lazy=True, cascade='all, delete-orphan')
    checkpoints = db.relationship('Checkpoint', backref='run', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'run_id': self.run_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None
        }
