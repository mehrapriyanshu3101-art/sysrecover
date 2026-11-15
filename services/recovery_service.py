import json
from database.dao import CheckpointDAO, RecoveryLogDAO, TransactionDAO


class RecoveryService:
    def current_lsn(self, run_id):
        """Log Sequence Number of the last log record written for this run"""
        logs = RecoveryLogDAO.get_by_run_id(run_id)
        return max((log['lsn'] for log in logs), default=0)

    def next_lsn(self, run_id):
        """Next Log Sequence Number for a run, based on the log on disk"""
        return self.current_lsn(run_id) + 1

    def create_checkpoint(self, run_id):
        """Create a checkpoint"""
        transactions = TransactionDAO.get_by_run_id(run_id)
        active_transactions = [t for t in transactions if t['status'] == 'active']
        active_ids = [t['transaction_id'] for t in active_transactions]

        # A checkpoint records the last log record it covers, so recovery looks at
        # records with a strictly greater LSN (the writes that came after it).
        lsn = self.current_lsn(run_id)
        checkpoint_id = CheckpointDAO.create(run_id, lsn, active_ids)
        checkpoint = CheckpointDAO.get_latest(run_id)

        return {
            'checkpoint_id': checkpoint_id,
            'run_id': run_id,
            'lsn': lsn,
            'timestamp': checkpoint['timestamp'] if checkpoint else None,
            'active_transactions': active_ids
        }

    def recover(self, run_id):
        """Perform UNDO/REDO recovery"""
        # Get latest checkpoint
        checkpoint = CheckpointDAO.get_latest(run_id)

        if not checkpoint:
            return {'message': 'No checkpoint found, full recovery needed'}

        active_at_checkpoint = []
        if checkpoint['active_transactions']:
            try:
                active_at_checkpoint = json.loads(checkpoint['active_transactions'])
            except (TypeError, ValueError):
                active_at_checkpoint = []

        # Get logs after checkpoint
        logs = RecoveryLogDAO.get_after_lsn(run_id, checkpoint['lsn'])

        undo_list = []
        redo_list = []

        for log in logs:
            if log['transaction_id'] in active_at_checkpoint:
                if log['operation'] == 'write':
                    undo_list.append(log)
            else:
                if log['operation'] == 'commit':
                    redo_list.append(log)

        return {
            'checkpoint_lsn': checkpoint['lsn'],
            'undo_count': len(undo_list),
            'redo_count': len(redo_list),
            'message': 'Recovery completed'
        }
