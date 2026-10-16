from flask import Blueprint, request, jsonify
from datetime import datetime
from models import SimulationRun
from database.connection import db

runs_bp = Blueprint('runs', __name__)

@runs_bp.route('/runs', methods=['GET'])
def get_runs():
    runs = SimulationRun.query.all()
    return jsonify([r.to_dict() for r in runs])

@runs_bp.route('/runs', methods=['POST'])
def create_run():
    data = request.get_json()
    run = SimulationRun(
        name=data.get('name'),
        description=data.get('description'),
        status='active'
    )
    db.session.add(run)
    db.session.commit()
    return jsonify(run.to_dict()), 201

@runs_bp.route('/runs/<int:run_id>', methods=['GET'])
def get_run(run_id):
    run = SimulationRun.query.get_or_404(run_id)
    return jsonify(run.to_dict())

@runs_bp.route('/runs/<int:run_id>', methods=['DELETE'])
def delete_run(run_id):
    run = SimulationRun.query.get_or_404(run_id)
    db.session.delete(run)
    db.session.commit()
    return jsonify({'message': 'Run deleted'})

@runs_bp.route('/runs/<int:run_id>/finish', methods=['POST'])
def finish_run(run_id):
    run = SimulationRun.query.get_or_404(run_id)
    run.status = 'finished'
    run.finished_at = datetime.utcnow()
    db.session.commit()
    return jsonify(run.to_dict())
