from flask import Blueprint
from .dashboard import dashboard_bp
from .runs import runs_bp
from .processes import processes_bp
from .scheduling import scheduling_bp
from .memory import memory_bp
from .transactions import transactions_bp
from .resources import resources_bp
from .deadlocks import deadlocks_bp
from .recovery import recovery_bp
from .diagnostics import diagnostics_bp
from .events import events_bp
from .reports import reports_bp

def register_blueprints(app):
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(runs_bp, url_prefix='/api')
    app.register_blueprint(processes_bp, url_prefix='/api')
    app.register_blueprint(scheduling_bp, url_prefix='/api')
    app.register_blueprint(memory_bp, url_prefix='/api')
    app.register_blueprint(transactions_bp, url_prefix='/api')
    app.register_blueprint(resources_bp, url_prefix='/api')
    app.register_blueprint(deadlocks_bp, url_prefix='/api')
    app.register_blueprint(recovery_bp, url_prefix='/api')
    app.register_blueprint(diagnostics_bp, url_prefix='/api')
    app.register_blueprint(events_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api')
