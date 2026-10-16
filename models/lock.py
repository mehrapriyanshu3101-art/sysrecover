from datetime import datetime
from database.connection import db

class Lock(db.Model):
    __tablename__ = 'lock'
    
    lock_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.resource_id'), nullable=False)
    lock_type = db.Column(db.String(20), nullable=False)  # shared, exclusive
    status = db.Column(db.String(20), default='granted')  # granted, waiting
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'lock_id': self.lock_id,
            'transaction_id': self.transaction_id,
            'resource_id': self.resource_id,
            'lock_type': self.lock_type,
            'status': self.status,
            'granted_at': self.granted_at.isoformat() if self.granted_at else None
        }
