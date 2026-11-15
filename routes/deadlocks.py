from flask import Blueprint, request, jsonify
from database.dao import SimulationRunDAO, TransactionDAO, LockDAO, EventLogDAO
from database.mysql_connection import db
from services.deadlock_service import DeadlockService

deadlocks_bp = Blueprint('deadlocks', __name__)

@deadlocks_bp.route('/runs/<int:run_id>/deadlocks/detect', methods=['POST'])
def detect_deadlocks(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404

    # Only locks belonging to this run take part in the wait-for graph
    locks = []
    for lock in LockDAO.get_all():
        trans = TransactionDAO.get_by_id(lock['transaction_id'])
        if trans and trans['run_id'] == run_id:
            locks.append(lock)

    service = DeadlockService()
    result = service.detect_deadlock(locks)

    if result['deadlock_detected']:
        EventLogDAO.create(
            run_id, 'deadlock', 'error',
            f"Deadlock detected between transactions {sorted(result['transactions'])}"
        )
    else:
        EventLogDAO.create(run_id, 'deadlock', 'info', 'Deadlock check: no deadlock detected')

    return jsonify(result)

@deadlocks_bp.route('/runs/<int:run_id>/deadlocks/recover', methods=['POST'])
def recover_deadlock(run_id):
    if not SimulationRunDAO.get_by_id(run_id):
        return jsonify({'error': 'Run not found'}), 404
    data = request.get_json() or {}

    victim_id = data.get('victim_transaction_id')
    if not victim_id:
        return jsonify({'error': 'victim_transaction_id is required'}), 400

    transaction = TransactionDAO.get_by_id(victim_id)
    if not transaction or transaction['run_id'] != run_id:
        return jsonify({'error': 'Transaction not found'}), 404

    # Abort the victim and release everything it holds
    released = 0
    freed_resources = set()
    for lock in LockDAO.get_all():
        if lock['transaction_id'] != victim_id:
            continue
        if lock['status'] == 'granted':
            db.execute_query(
                "UPDATE resource SET available_instances = available_instances + 1 WHERE resource_id = %s",
                (lock['resource_id'],), fetch=False
            )
            freed_resources.add(lock['resource_id'])
        LockDAO.delete(lock['lock_id'])
        released += 1

    # Hand the freed instances to transactions that were queued behind the victim
    for resource_id in freed_resources:
        LockDAO.grant_next_waiting(resource_id)

    db.execute_query(
        "UPDATE transactions SET status = 'aborted', rollback_time = NOW(), "
        "two_phase_state = 'aborted' WHERE transaction_id = %s",
        (victim_id,), fetch=False
    )

    EventLogDAO.create(
        run_id, 'deadlock', 'warning',
        f"Transaction {victim_id} aborted to resolve deadlock ({released} lock(s) released)"
    )

    return jsonify({
        'message': f'Transaction {victim_id} aborted to resolve deadlock',
        'victim_transaction_id': victim_id,
        'locks_released': released
    })
