from models import Lock, Resource
from database.connection import db

class LockManager:
    def __init__(self):
        pass
    
    def request_lock(self, transaction_id, resource_id, lock_type):
        """Request a lock on a resource"""
        resource = Resource.query.get(resource_id)
        
        # Check if lock can be granted
        existing_locks = Lock.query.filter_by(resource_id=resource_id, status='granted').all()
        
        can_grant = True
        for lock in existing_locks:
            if lock.transaction_id == transaction_id:
                # Already has lock
                return {'granted': True, 'message': 'Already has lock'}
            
            if lock_type == 'exclusive' or lock.lock_type == 'exclusive':
                can_grant = False
                break
        
        if can_grant and resource.available_instances > 0:
            # Grant lock
            new_lock = Lock(
                transaction_id=transaction_id,
                resource_id=resource_id,
                lock_type=lock_type,
                status='granted'
            )
            resource.available_instances -= 1
            db.session.add(new_lock)
            db.session.commit()
            
            return {'granted': True, 'lock_id': new_lock.lock_id}
        else:
            # Put in waiting state
            waiting_lock = Lock(
                transaction_id=transaction_id,
                resource_id=resource_id,
                lock_type=lock_type,
                status='waiting'
            )
            db.session.add(waiting_lock)
            db.session.commit()
            
            return {'granted': False, 'lock_id': waiting_lock.lock_id}
    
    def release_lock(self, lock_id):
        """Release a lock"""
        lock = Lock.query.get(lock_id)
        if lock:
            resource = Resource.query.get(lock.resource_id)
            resource.available_instances += 1
            db.session.delete(lock)
            db.session.commit()
            return {'released': True}
        return {'released': False}
    
    def check_conflict(self, transaction_id, resource_id, lock_type):
        """Check if lock request would conflict"""
        existing_locks = Lock.query.filter_by(
            resource_id=resource_id,
            status='granted'
        ).all()
        
        for lock in existing_locks:
            if lock.transaction_id != transaction_id:
                if lock_type == 'exclusive' or lock.lock_type == 'exclusive':
                    return True
        return False
