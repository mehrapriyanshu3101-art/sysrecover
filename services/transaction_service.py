from database.dao import TransactionDAO
from database.mysql_connection import db

class TransactionService:
    def __init__(self):
        self.data_store = {'A': 100, 'B': 200}
        self.lsn_counter = 0
    
    def read(self, transaction_id, data_item):
        """Simulate read operation"""
        value = self.data_store.get(data_item, 0)
        return {
            'transaction_id': transaction_id,
            'operation': 'read',
            'data_item': data_item,
            'value': value
        }
    
    def write(self, transaction_id, run_id, data_item, new_value):
        """Simulate write operation with logging"""
        old_value = self.data_store.get(data_item, 0)
        self.data_store[data_item] = new_value
        
        # Write-ahead log
        self.lsn_counter += 1
        query = """
            INSERT INTO recovery_log (run_id, transaction_id, lsn, operation, data_item, old_value, new_value)
            VALUES (%s, %s, %s, 'write', %s, %s, %s)
        """
        db.execute_query(query, (run_id, transaction_id, self.lsn_counter, data_item, str(old_value), str(new_value)), fetch=False)
        
        return {
            'transaction_id': transaction_id,
            'operation': 'write',
            'data_item': data_item,
            'old_value': old_value,
            'new_value': new_value
        }
    
    def commit(self, transaction_id):
        """Commit transaction"""
        TransactionDAO.commit(transaction_id)
        
        # Log commit
        trans = TransactionDAO.get_by_id(transaction_id)
        if trans:
            self.lsn_counter += 1
            query = """
                INSERT INTO recovery_log (run_id, transaction_id, lsn, operation)
                VALUES (%s, %s, %s, 'commit')
            """
            db.execute_query(query, (trans['run_id'], transaction_id, self.lsn_counter), fetch=False)
        
        return {
            'transaction_id': transaction_id,
            'status': 'committed',
            'message': 'Transaction committed successfully'
        }
    
    def rollback(self, transaction_id):
        """Rollback transaction"""
        TransactionDAO.rollback(transaction_id)
        
        # Log rollback
        trans = TransactionDAO.get_by_id(transaction_id)
        if trans:
            self.lsn_counter += 1
            query = """
                INSERT INTO recovery_log (run_id, transaction_id, lsn, operation)
                VALUES (%s, %s, %s, 'abort')
            """
            db.execute_query(query, (trans['run_id'], transaction_id, self.lsn_counter), fetch=False)
        
        return {
            'transaction_id': transaction_id,
            'status': 'aborted',
            'message': 'Transaction rolled back'
        }
