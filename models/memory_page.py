from database.connection import db

class MemoryPage(db.Model):
    __tablename__ = 'memory_page'
    
    page_id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('simulation_run.run_id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    frame_number = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='not_in_memory')  # not_in_memory, in_memory, referenced
    last_accessed = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'page_id': self.page_id,
            'run_id': self.run_id,
            'page_number': self.page_number,
            'frame_number': self.frame_number,
            'status': self.status,
            'last_accessed': self.last_accessed
        }
