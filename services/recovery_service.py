from datetime import datetime
import json
from models import Checkpoint, RecoveryLog, Transaction
from database.connection import db

class RecoveryService:
    def __init__(self):
        self.lsn_counter = 0
    
    def create_checkpoint(self, run_id):
        """Create a checkpoint"""
        active_transactions = Transaction.query.filter_by(run_id=run_id, status='active').all()
        active_ids = [t.transaction_id for t in active_transactions]
        
        checkpoint = Checkpoint(
            run_id=run_id,
            lsn=self.lsn_counter,
            active_transactions=json.dumps(active_ids)
        )
        db.session.add(checkpoint)
        db.session.commit()
        
        return checkpoint
    
    def recover(self, run_id):
        """Perform UNDO/REDO recovery"""
        # Get latest checkpoint
        checkpoint = Checkpoint.query.filter_by(run_id=run_id).order_by(Checkpoint.timestamp.desc()).first()
        
        if not checkpoint:
            return {'message': 'No checkpoint found, full recovery needed'}
        
        active_at_checkpoint = json.loads(checkpoint.active_transactions)
        
        # Get logs after checkpoint
        logs = RecoveryLog.query.filter(
            RecoveryLog.run_id == run_id,
            RecoveryLog.lsn > checkpoint.lsn
        ).order_by(RecoveryLog.lsn).all()
        
        undo_list = []
        redo_list = []
        
        for log in logs:
            if log.transaction_id in active_at_checkpoint:
                if log.operation == 'write':
                    undo_list.append(log)
            else:
                if log.operation == 'commit':
                    redo_list.append(log)
        
        # Perform UNDO
        for log in undo_list:
            # In real system, would restore old_value
            pass
        
        # Perform REDO
        for log in redo_list:
            # In real system, would apply new_value
            pass
        
        return {
            'checkpoint_lsn': checkpoint.lsn,
            'undo_count': len(undo_list),
            'redo_count': len(redo_list),
            'message': 'Recovery completed'
        }
