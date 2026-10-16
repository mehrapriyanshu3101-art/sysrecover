from models import Lock, Transaction
from database.connection import db

class DeadlockService:
    def detect_deadlock(self, locks):
        """Detect deadlock using wait-for graph"""
        # Build wait-for graph
        graph = {}
        
        for lock in locks:
            if lock.status == 'waiting':
                # Transaction is waiting for a resource
                waiting_for = lock.transaction_id
                
                # Find who holds the resource
                holders = Lock.query.filter_by(
                    resource_id=lock.resource_id,
                    status='granted'
                ).all()
                
                for holder in holders:
                    if waiting_for not in graph:
                        graph[waiting_for] = []
                    graph[waiting_for].append(holder.transaction_id)
        
        # Detect cycle
        has_cycle = self.detect_cycle(graph)
        
        if has_cycle:
            return {
                'deadlock_detected': True,
                'graph': graph,
                'message': 'Deadlock存在于等待图中'
            }
        
        return {
            'deadlock_detected': False,
            'graph': graph,
            'message': 'No deadlock detected'
        }
    
    def detect_cycle(self, graph):
        """Detect cycle in directed graph using DFS"""
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            neighbors = graph.get(node, [])
            for neighbor in neighbors:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False
    
    def find_victim(self, graph):
        """Find a victim transaction to abort"""
        # Simple strategy: abort the transaction with most locks
        max_locks = 0
        victim = None
        
        for node in graph:
            lock_count = Lock.query.filter_by(transaction_id=node).count()
            if lock_count > max_locks:
                max_locks = lock_count
                victim = node
        
        return victim
