from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO, ResourceDAO
from services.system_resource_service import SystemResourceService

resources_bp = Blueprint('resources', __name__)

@resources_bp.route('/runs/<int:run_id>/resources', methods=['GET'])
def get_resources(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    resources = ResourceDAO.get_by_run_id(run_id)
    return jsonify([ResourceDAO.to_dict(r) for r in resources])

@resources_bp.route('/runs/<int:run_id>/resources', methods=['POST'])
def create_resource(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    data = request.get_json()
    
    resource = ResourceDAO.create(
        run_id=run_id,
        resource_name=data.get('resource_name'),
        resource_type=data.get('resource_type', 'general'),
        total_instances=data.get('total_instances', 1)
    )
    return jsonify(ResourceDAO.to_dict(resource)), 201

@resources_bp.route('/runs/<int:run_id>/resources/auto-import', methods=['POST'])
def auto_import_resources(run_id):
    """Automatically import system resources"""
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    
    service = SystemResourceService()
    system_resources = service.get_system_resources()
    
    imported = []
    for res_data in system_resources:
        resource = ResourceDAO.create(
            run_id=run_id,
            resource_name=res_data['resource_name'],
            resource_type=res_data['resource_type'],
            total_instances=res_data['total_instances']
        )
        imported.append(resource)
    
    return jsonify({
        'message': f'Imported {len(imported)} system resources',
        'resources': [ResourceDAO.to_dict(r) for r in imported]
    }), 201
