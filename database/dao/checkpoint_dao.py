from database.mysql_connection import db

class CheckpointDAO:
    """Data Access Object for Checkpoint table"""

    @staticmethod
    def get_by_run_id(run_id):
        """Get all checkpoints for a simulation run"""
        query = "SELECT * FROM checkpoint WHERE run_id = %s ORDER BY checkpoint_id DESC"
        return db.execute_query(query, (run_id,))

    @staticmethod
    def get_latest(run_id):
        """Get the latest checkpoint for a run"""
        query = "SELECT * FROM checkpoint WHERE run_id = %s ORDER BY checkpoint_id DESC LIMIT 1"
        result = db.execute_query(query, (run_id,))
        return result[0] if result else None

    @staticmethod
    def create(run_id, lsn, active_transactions):
        """Create a new checkpoint"""
        import json
        query = """
            INSERT INTO checkpoint (run_id, lsn, active_transactions)
            VALUES (%s, %s, %s)
        """
        checkpoint_id = db.execute_query(query, (run_id, lsn, json.dumps(active_transactions)), fetch=False)
        return checkpoint_id

    @staticmethod
    def to_dict(checkpoint):
        """Convert database row to dictionary"""
        return {
            'checkpoint_id': checkpoint['checkpoint_id'],
            'run_id': checkpoint['run_id'],
            'lsn': checkpoint['lsn'],
            'timestamp': checkpoint['timestamp'],
            'active_transactions': checkpoint['active_transactions']
        }
