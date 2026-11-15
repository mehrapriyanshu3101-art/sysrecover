from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO, ResourceDAO, LockDAO, TransactionDAO, EventLogDAO
from database.mysql_connection import db
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
    data = request.get_json() or {}

    if not data.get('resource_name'):
        return jsonify({'error': 'Resource name is required'}), 400

    total_instances = max(1, int(data.get('total_instances', 1)))

    resource = ResourceDAO.create(
        run_id=run_id,
        resource_name=data.get('resource_name'),
        resource_type=data.get('resource_type', 'general'),
        total_instances=total_instances
    )
    EventLogDAO.create(
        run_id, 'system', 'info',
        f"Resource '{resource['resource_name']}' created with {total_instances} instance(s)"
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

    EventLogDAO.create(
        run_id, 'system', 'info',
        f"Imported {len(imported)} system resources"
    )
    return jsonify({
        'message': f'Imported {len(imported)} system resources',
        'resources': [ResourceDAO.to_dict(r) for r in imported]
    }), 201

@resources_bp.route('/runs/<int:run_id>/resources/<int:resource_id>', methods=['DELETE'])
def delete_resource(run_id, resource_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404

    resource = ResourceDAO.get_by_id(resource_id)
    if not resource or resource['run_id'] != run_id:
        return jsonify({'error': 'Resource not found'}), 404

    ResourceDAO.delete(resource_id)
    EventLogDAO.create(
        run_id, 'system', 'warning',
        f"Resource '{resource['resource_name']}' deleted"
    )
    return jsonify({'message': 'Resource deleted'})

@resources_bp.route('/runs/<int:run_id>/locks', methods=['GET'])
def get_locks(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    locks = LockDAO.get_all()
    # Filter locks for this run by checking transaction's run_id
    run_locks = []
    for lock in locks:
        trans = TransactionDAO.get_by_id(lock['transaction_id'])
        if trans and trans['run_id'] == run_id:
            run_locks.append(lock)
    return jsonify([LockDAO.to_dict(l) for l in run_locks])

@resources_bp.route('/runs/<int:run_id>/locks', methods=['POST'])
def create_lock(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    data = request.get_json() or {}

    transaction_id = data.get('transaction_id')
    resource_id = data.get('resource_id')
    lock_type = data.get('lock_type', 'shared')

    if not transaction_id or not resource_id:
        return jsonify({'error': 'transaction_id and resource_id are required'}), 400

    # Verify transaction belongs to this run
    trans = TransactionDAO.get_by_id(transaction_id)
    if not trans or trans['run_id'] != run_id:
        return jsonify({'error': 'Transaction not found or does not belong to this run'}), 404

    if trans['status'] != 'active':
        return jsonify({'error': 'Only active transactions can request locks'}), 400

    # Verify resource belongs to this run
    resource = ResourceDAO.get_by_id(resource_id)
    if not resource or resource['run_id'] != run_id:
        return jsonify({'error': 'Resource not found or does not belong to this run'}), 404

    # Check if resource has available instances
    if resource['available_instances'] <= 0:
        # Create waiting lock
        lock = LockDAO.create(transaction_id, resource_id, lock_type)
        db.execute_query("UPDATE locks SET status = 'waiting' WHERE lock_id = %s", (lock['lock_id'],), fetch=False)
        waiting_lock = LockDAO.get_by_id(lock['lock_id'])
        EventLogDAO.create(
            run_id, 'transaction', 'warning',
            f"Transaction {transaction_id} waiting for {resource['resource_name']} "
            f"({lock_type} lock)"
        )
        return jsonify({'message': 'Lock request queued (waiting)', 'lock': LockDAO.to_dict(waiting_lock)}), 201

    # Create granted lock
    lock = LockDAO.create(transaction_id, resource_id, lock_type)
    # Decrease available instances
    db.execute_query(
        "UPDATE resource SET available_instances = available_instances - 1 WHERE resource_id = %s",
        (resource_id,), fetch=False
    )
    EventLogDAO.create(
        run_id, 'transaction', 'info',
        f"Transaction {transaction_id} granted {lock_type} lock on {resource['resource_name']}"
    )
    return jsonify({'message': 'Lock granted', 'lock': LockDAO.to_dict(lock)}), 201

@resources_bp.route('/runs/<int:run_id>/locks/<int:lock_id>', methods=['DELETE'])
def delete_lock(run_id, lock_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404

    lock = LockDAO.get_by_id(lock_id)
    if not lock:
        return jsonify({'error': 'Lock not found'}), 404

    # Verify transaction belongs to this run
    trans = TransactionDAO.get_by_id(lock['transaction_id'])
    if not trans or trans['run_id'] != run_id:
        return jsonify({'error': 'Lock does not belong to this run'}), 404

    # If lock was granted, increase available instances and let a waiter in
    if lock['status'] == 'granted':
        db.execute_query(
            "UPDATE resource SET available_instances = available_instances + 1 WHERE resource_id = %s",
            (lock['resource_id'],), fetch=False
        )
        granted = LockDAO.grant_next_waiting(lock['resource_id'])
        if granted:
            EventLogDAO.create(
                run_id, 'transaction', 'info',
                f"Waiting lock of transaction {granted['transaction_id']} granted after release"
            )

    LockDAO.delete(lock_id)
    EventLogDAO.create(
        run_id, 'transaction', 'info',
        f"Lock {lock_id} released by transaction {lock['transaction_id']}"
    )
    return jsonify({'message': 'Lock released'})
