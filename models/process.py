from datetime import datetime
from database.connection import db

class Process(db.Model):
    __tablename__ = 'process'
    
    process_id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('simulation_run.run_id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    arrival_time = db.Column(db.Integer, default=0)
    burst_time = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, default=0)
    state = db.Column(db.String(20), default='ready')  # ready, running, completed
    completion_time = db.Column(db.Integer)
    turnaround_time = db.Column(db.Integer)
    waiting_time = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'process_id': self.process_id,
            'run_id': self.run_id,
            'name': self.name,
            'arrival_time': self.arrival_time,
            'burst_time': self.burst_time,
            'priority': self.priority,
            'state': self.state,
            'completion_time': self.completion_time,
            'turnaround_time': self.turnaround_time,
            'waiting_time': self.waiting_time
        }
