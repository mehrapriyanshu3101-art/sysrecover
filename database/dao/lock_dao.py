from database.mysql_connection import db

class LockDAO:
    """Data Access Object for Lock table"""
    
    @staticmethod
    def get_all():
        """Get all locks"""
        query = "SELECT * FROM locks ORDER BY lock_id"
        return db.execute_query(query)
    
    @staticmethod
    def get_by_id(lock_id):
        """Get lock by ID"""
        query = "SELECT * FROM locks WHERE lock_id = %s"
        result = db.execute_query(query, (lock_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_waiting_locks():
        """Get all locks with waiting status"""
        query = "SELECT * FROM locks WHERE status = 'waiting'"
        return db.execute_query(query)
    
    @staticmethod
    def create(transaction_id, resource_id, lock_type):
        """Create a new lock"""
        query = """
            INSERT INTO locks (transaction_id, resource_id, lock_type, status, granted_at)
            VALUES (%s, %s, %s, 'granted', NOW())
        """
        lock_id = db.execute_query(query, (transaction_id, resource_id, lock_type), fetch=False)
        return LockDAO.get_by_id(lock_id)
    
    @staticmethod
    def delete(lock_id):
        """Delete a lock"""
        query = "DELETE FROM locks WHERE lock_id = %s"
        db.execute_query(query, (lock_id,), fetch=False)
    
    @staticmethod
    def to_dict(lock):
        """Convert database row to dictionary"""
        return {
            'lock_id': lock['lock_id'],
            'transaction_id': lock['transaction_id'],
            'resource_id': lock['resource_id'],
            'lock_type': lock['lock_type'],
            'status': lock['status'],
            'granted_at': lock['granted_at'].isoformat() if lock['granted_at'] else None
        }
