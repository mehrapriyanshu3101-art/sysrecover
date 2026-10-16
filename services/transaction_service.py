from datetime import datetime
from models import RecoveryLog
from database.connection import db

class TransactionService:
    def __init__(self):
        self.data_store = {'A': 100, 'B': 200}
        self.lsn_counter = 0
    
    def read(self, transaction, data_item):
        """Simulate read operation"""
        value = self.data_store.get(data_item, 0)
        return {
            'transaction_id': transaction.transaction_id,
            'operation': 'read',
            'data_item': data_item,
            'value': value
        }
    
    def write(self, transaction, data_item, new_value):
        """Simulate write operation with logging"""
        old_value = self.data_store.get(data_item, 0)
        self.data_store[data_item] = new_value
        
        # Write-ahead log
        self.lsn_counter += 1
        log = RecoveryLog(
            run_id=transaction.run_id,
            transaction_id=transaction.transaction_id,
            lsn=self.lsn_counter,
            operation='write',
            data_item=data_item,
            old_value=str(old_value),
            new_value=str(new_value)
        )
        db.session.add(log)
        db.session.commit()
        
        return {
            'transaction_id': transaction.transaction_id,
            'operation': 'write',
            'data_item': data_item,
            'old_value': old_value,
            'new_value': new_value
        }
    
    def commit(self, transaction):
        """Commit transaction"""
        transaction.status = 'committed'
        transaction.commit_time = datetime.utcnow()
        transaction.two_phase_state = 'shrinking'
        
        # Log commit
        self.lsn_counter += 1
        log = RecoveryLog(
            run_id=transaction.run_id,
            transaction_id=transaction.transaction_id,
            lsn=self.lsn_counter,
            operation='commit'
        )
        db.session.add(log)
        db.session.commit()
        
        return {
            'transaction_id': transaction.transaction_id,
            'status': 'committed',
            'message': 'Transaction committed successfully'
        }
    
    def rollback(self, transaction):
        """Rollback transaction"""
        transaction.status = 'aborted'
        transaction.rollback_time = datetime.utcnow()
        
        # Log rollback
        self.lsn_counter += 1
        log = RecoveryLog(
            run_id=transaction.run_id,
            transaction_id=transaction.transaction_id,
            lsn=self.lsn_counter,
            operation='abort'
        )
        db.session.add(log)
        db.session.commit()
        
        return {
            'transaction_id': transaction.transaction_id,
            'status': 'aborted',
            'message': 'Transaction rolled back'
        }
