import json

from database.dao import TransactionDAO
from database.mysql_connection import db


class TransactionService:
    """Simulated data store shared by all transactions (process-wide)"""

    data_store = {'A': 100, 'B': 200}

    def next_lsn(self, run_id):
        """Next Log Sequence Number for a run, based on the write-ahead log"""
        result = db.execute_query(
            "SELECT COALESCE(MAX(lsn), 0) as max_lsn FROM recovery_log WHERE run_id = %s",
            (run_id,)
        )
        current = result[0]['max_lsn'] if result else 0
        return (current or 0) + 1

    def read(self, transaction_id, data_item):
        """Simulate read operation"""
        value = self.data_store.get(data_item, 0)
        return {
            'transaction_id': transaction_id,
            'operation': 'read',
            'data_item': data_item,
            'value': value,
            'data_store': dict(self.data_store)
        }

    def write(self, transaction_id, run_id, data_item, new_value):
        """Simulate write operation with logging"""
        old_value = self.data_store.get(data_item, 0)
        self.data_store[data_item] = new_value

        # Write-ahead log
        lsn = self.next_lsn(run_id)
        query = """
            INSERT INTO recovery_log (run_id, transaction_id, lsn, operation, data_item, old_value, new_value)
            VALUES (%s, %s, %s, 'write', %s, %s, %s)
        """
        db.execute_query(
            query,
            (run_id, transaction_id, lsn, data_item, str(old_value), str(new_value)),
            fetch=False
        )

        return {
            'transaction_id': transaction_id,
            'operation': 'write',
            'data_item': data_item,
            'old_value': old_value,
            'new_value': new_value,
            'lsn': lsn,
            'data_store': dict(self.data_store)
        }

    def commit(self, transaction_id):
        """Commit transaction"""
        trans = TransactionDAO.get_by_id(transaction_id)
        TransactionDAO.commit(transaction_id)

        if trans:
            lsn = self.next_lsn(trans['run_id'])
            query = """
                INSERT INTO recovery_log (run_id, transaction_id, lsn, operation)
                VALUES (%s, %s, %s, 'commit')
            """
            db.execute_query(query, (trans['run_id'], transaction_id, lsn), fetch=False)

        return {
            'transaction_id': transaction_id,
            'status': 'committed',
            'message': 'Transaction committed successfully'
        }

    def rollback(self, transaction_id):
        """Rollback transaction"""
        trans = TransactionDAO.get_by_id(transaction_id)
        TransactionDAO.rollback(transaction_id)

        if trans:
            lsn = self.next_lsn(trans['run_id'])
            query = """
                INSERT INTO recovery_log (run_id, transaction_id, lsn, operation)
                VALUES (%s, %s, %s, 'abort')
            """
            db.execute_query(query, (trans['run_id'], transaction_id, lsn), fetch=False)

        return {
            'transaction_id': transaction_id,
            'status': 'aborted',
            'message': 'Transaction rolled back'
        }
