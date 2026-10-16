from flask import Flask, render_template, jsonify
from config import Config
from database import init_db
from routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Main routes
    @app.route('/')
    def index():
        return render_template('dashboard.html')
    
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy', 'message': 'SysRecover API is running'})
    
    # Template routes
    @app.route('/runs')
    def runs_page():
        return render_template('runs.html')
    
    @app.route('/processes')
    def processes_page():
        return render_template('processes.html')
    
    @app.route('/scheduling')
    def scheduling_page():
        return render_template('scheduling.html')
    
    @app.route('/memory')
    def memory_page():
        return render_template('memory.html')
    
    @app.route('/transactions')
    def transactions_page():
        return render_template('transactions.html')
    
    @app.route('/resources')
    def resources_page():
        return render_template('resources.html')
    
    @app.route('/deadlocks')
    def deadlocks_page():
        return render_template('deadlocks.html')
    
    @app.route('/recovery')
    def recovery_page():
        return render_template('recovery.html')
    
    @app.route('/diagnostics')
    def diagnostics_page():
        return render_template('diagnostics.html')
    
    @app.route('/events')
    def events_page():
        return render_template('events.html')
    
    @app.route('/reports')
    def reports_page():
        return render_template('reports.html')
    
    @app.route('/about')
    def about_page():
        return render_template('about.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
