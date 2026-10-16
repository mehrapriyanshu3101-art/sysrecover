from flask import Blueprint, request, jsonify
from models import SimulationRun, Resource
from database.connection import db

resources_bp = Blueprint('resources', __name__)

@resources_bp.route('/runs/<int:run_id>/resources', methods=['GET'])
def get_resources(run_id):
    SimulationRun.query.get_or_404(run_id)
    resources = Resource.query.filter_by(run_id=run_id).all()
    return jsonify([r.to_dict() for r in resources])

@resources_bp.route('/runs/<int:run_id>/resources', methods=['POST'])
def create_resource(run_id):
    SimulationRun.query.get_or_404(run_id)
    data = request.get_json()
    
    resource = Resource(
        run_id=run_id,
        resource_name=data.get('resource_name'),
        resource_type=data.get('resource_type', 'general'),
        total_instances=data.get('total_instances', 1),
        available_instances=data.get('total_instances', 1)
    )
    db.session.add(resource)
    db.session.commit()
    return jsonify(resource.to_dict()), 201
