from database.mysql_connection import db

class TransactionDAO:
    """Data Access Object for Transaction table"""
    
    @staticmethod
    def get_by_run_id(run_id):
        """Get all transactions for a simulation run"""
        query = "SELECT * FROM transactions WHERE run_id = %s ORDER BY transaction_id"
        return db.execute_query(query, (run_id,))
    
    @staticmethod
    def get_by_id(transaction_id):
        """Get transaction by ID"""
        query = "SELECT * FROM transactions WHERE transaction_id = %s"
        result = db.execute_query(query, (transaction_id,))
        return result[0] if result else None
    
    @staticmethod
    def create(run_id, trans_type, process_id):
        """Create a new transaction"""
        query = """
            INSERT INTO transactions (run_id, type, process_id, status, two_phase_state)
            VALUES (%s, %s, %s, 'active', 'growing')
        """
        transaction_id = db.execute_query(query, (run_id, trans_type, process_id), fetch=False)
        return TransactionDAO.get_by_id(transaction_id)
    
    @staticmethod
    def commit(transaction_id):
        """Commit a transaction"""
        query = """
            UPDATE transactions 
            SET status = 'committed', commit_time = NOW(), two_phase_state = 'committed'
            WHERE transaction_id = %s
        """
        db.execute_query(query, (transaction_id,), fetch=False)
        return TransactionDAO.get_by_id(transaction_id)
    
    @staticmethod
    def rollback(transaction_id):
        """Rollback a transaction"""
        query = """
            UPDATE transactions 
            SET status = 'aborted', rollback_time = NOW(), two_phase_state = 'aborted'
            WHERE transaction_id = %s
        """
        db.execute_query(query, (transaction_id,), fetch=False)
        return TransactionDAO.get_by_id(transaction_id)
    
    @staticmethod
    def to_dict(transaction):
        """Convert database row to dictionary"""
        return {
            'transaction_id': transaction['transaction_id'],
            'run_id': transaction['run_id'],
            'process_id': transaction['process_id'],
            'type': transaction['type'],
            'status': transaction['status'],
            'start_time': transaction['start_time'].isoformat() if transaction['start_time'] else None,
            'commit_time': transaction['commit_time'].isoformat() if transaction['commit_time'] else None,
            'rollback_time': transaction['rollback_time'].isoformat() if transaction['rollback_time'] else None,
            'two_phase_state': transaction['two_phase_state']
        }
