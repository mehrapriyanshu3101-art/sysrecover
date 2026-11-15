from database.dao import LockDAO
from database.mysql_connection import db

class DeadlockService:
    def detect_deadlock(self, locks):
        """Detect deadlock using a wait-for graph built from the given locks"""
        # Build wait-for graph: waiting transaction -> transaction holding the resource
        graph = {}

        for lock in locks:
            if lock['status'] != 'waiting':
                continue

            waiting_for = lock['transaction_id']

            query = "SELECT * FROM locks WHERE resource_id = %s AND status = 'granted'"
            holders = db.execute_query(query, (lock['resource_id'],))

            for holder in holders:
                if holder['transaction_id'] == waiting_for:
                    continue
                graph.setdefault(waiting_for, [])
                if holder['transaction_id'] not in graph[waiting_for]:
                    graph[waiting_for].append(holder['transaction_id'])

        # Detect cycle
        cycle = self.find_cycle(graph)

        if cycle:
            return {
                'deadlock_detected': True,
                'graph': graph,
                'transactions': cycle,
                'message': 'Deadlock detected: ' + ' -> '.join(f'T{node}' for node in cycle)
            }

        return {
            'deadlock_detected': False,
            'graph': graph,
            'transactions': [],
            'message': 'No deadlock detected'
        }

    def find_cycle(self, graph):
        """Return the first cycle found in the graph, or None"""
        visited = set()
        path = []

        def dfs(node):
            if node in path:
                return path[path.index(node):] + [node]

            if node in visited:
                return None

            visited.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                cycle = dfs(neighbor)
                if cycle:
                    return cycle

            path.pop()
            return None

        for node in graph:
            cycle = dfs(node)
            if cycle:
                return cycle

        return None

    def detect_cycle(self, graph):
        """Detect cycle in directed graph using DFS"""
        return self.find_cycle(graph) is not None

    def find_victim(self, graph):
        """Find a victim transaction to abort (the one holding the most locks)"""
        max_locks = 0
        victim = None

        for node in self.get_cycle_nodes(graph):
            query = "SELECT COUNT(*) as count FROM locks WHERE transaction_id = %s AND status = 'granted'"
            result = db.execute_query(query, (node,))
            lock_count = result[0]['count'] if result else 0
            if lock_count > max_locks:
                max_locks = lock_count
                victim = node

        return victim

    def get_cycle_nodes(self, graph):
        """Unique transaction ids that are part of a deadlock cycle"""
        cycle = self.find_cycle(graph)
        if not cycle:
            return []
        return list(dict.fromkeys(cycle))
