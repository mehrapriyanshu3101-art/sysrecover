from database.mysql_connection import db

class RecoveryLogDAO:
    """Data Access Object for RecoveryLog table"""
    
    @staticmethod
    def get_by_run_id(run_id):
        """Get all recovery logs for a simulation run"""
        query = "SELECT * FROM recovery_log WHERE run_id = %s ORDER BY lsn"
        return db.execute_query(query, (run_id,))
    
    @staticmethod
    def get_after_lsn(run_id, lsn):
        """Get all logs after a specific LSN"""
        query = "SELECT * FROM recovery_log WHERE run_id = %s AND lsn > %s ORDER BY lsn"
        return db.execute_query(query, (run_id, lsn))
    
    @staticmethod
    def create(run_id, transaction_id, lsn, operation, data_item=None, old_value=None, new_value=None):
        """Create a new recovery log entry"""
        query = """
            INSERT INTO recovery_log (run_id, transaction_id, lsn, operation, data_item, old_value, new_value)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        log_id = db.execute_query(query, (run_id, transaction_id, lsn, operation, data_item, old_value, new_value), fetch=False)
        return log_id
    
    @staticmethod
    def to_dict(log):
        """Convert database row to dictionary"""
        return {
            'log_id': log['log_id'],
            'run_id': log['run_id'],
            'transaction_id': log['transaction_id'],
            'lsn': log['lsn'],
            'operation': log['operation'],
            'data_item': log['data_item'],
            'old_value': log['old_value'],
            'new_value': log['new_value'],
            'timestamp': log['timestamp']
        }
