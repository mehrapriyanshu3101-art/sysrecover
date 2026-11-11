from database.mysql_connection import db

class SimulationRunDAO:
    """Data Access Object for Simulation Run table"""
    
    @staticmethod
    def get_all():
        """Get all simulation runs"""
        query = "SELECT * FROM simulation_run ORDER BY created_at DESC"
        return db.execute_query(query)
    
    @staticmethod
    def get_by_id(run_id):
        """Get simulation run by ID"""
        query = "SELECT * FROM simulation_run WHERE run_id = %s"
        result = db.execute_query(query, (run_id,))
        return result[0] if result else None
    
    @staticmethod
    def create(name, description):
        """Create a new simulation run"""
        query = """
            INSERT INTO simulation_run (name, description, status)
            VALUES (%s, %s, 'active')
        """
        run_id = db.execute_query(query, (name, description), fetch=False)
        return SimulationRunDAO.get_by_id(run_id)
    
    @staticmethod
    def delete(run_id):
        """Delete a simulation run"""
        query = "DELETE FROM simulation_run WHERE run_id = %s"
        db.execute_query(query, (run_id,), fetch=False)
    
    @staticmethod
    def finish(run_id):
        """Mark a simulation run as finished"""
        query = """
            UPDATE simulation_run 
            SET status = 'finished', finished_at = NOW()
            WHERE run_id = %s
        """
        db.execute_query(query, (run_id,), fetch=False)
        return SimulationRunDAO.get_by_id(run_id)
    
    @staticmethod
    def to_dict(run):
        """Convert database row to dictionary"""
        return {
            'run_id': run['run_id'],
            'name': run['name'],
            'description': run['description'],
            'status': run['status'],
            'created_at': run['created_at'].isoformat() if run['created_at'] else None,
            'finished_at': run['finished_at'].isoformat() if run['finished_at'] else None
        }
