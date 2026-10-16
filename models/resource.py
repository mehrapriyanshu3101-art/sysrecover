from database.connection import db

class Resource(db.Model):
    __tablename__ = 'resource'
    
    resource_id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('simulation_run.run_id'), nullable=False)
    resource_name = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(50), default='general')
    total_instances = db.Column(db.Integer, default=1)
    available_instances = db.Column(db.Integer, default=1)
    
    # Relationships
    locks = db.relationship('Lock', backref='resource', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'resource_id': self.resource_id,
            'run_id': self.run_id,
            'resource_name': self.resource_name,
            'resource_type': self.resource_type,
            'total_instances': self.total_instances,
            'available_instances': self.available_instances
        }
