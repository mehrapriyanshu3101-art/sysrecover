from database.mysql_connection import db

class ProcessDAO:
    """Data Access Object for Process table"""
    
    @staticmethod
    def get_by_run_id(run_id):
        """Get all processes for a simulation run"""
        query = "SELECT * FROM process WHERE run_id = %s ORDER BY process_id"
        return db.execute_query(query, (run_id,))
    
    @staticmethod
    def get_by_id(process_id):
        """Get process by ID"""
        query = "SELECT * FROM process WHERE process_id = %s"
        result = db.execute_query(query, (process_id,))
        return result[0] if result else None
    
    @staticmethod
    def create(run_id, name, arrival_time, burst_time, priority):
        """Create a new process"""
        query = """
            INSERT INTO process (run_id, name, arrival_time, burst_time, priority, state)
            VALUES (%s, %s, %s, %s, %s, 'ready')
        """
        process_id = db.execute_query(query, (run_id, name, arrival_time, burst_time, priority), fetch=False)
        return ProcessDAO.get_by_id(process_id)
    
    @staticmethod
    def delete(process_id):
        """Delete a process"""
        query = "DELETE FROM process WHERE process_id = %s"
        db.execute_query(query, (process_id,), fetch=False)
    
    @staticmethod
    def update_metrics(process_id, completion_time, turnaround_time, waiting_time):
        """Update process metrics after scheduling"""
        query = """
            UPDATE process 
            SET completion_time = %s, turnaround_time = %s, waiting_time = %s, state = 'completed'
            WHERE process_id = %s
        """
        db.execute_query(query, (completion_time, turnaround_time, waiting_time, process_id), fetch=False)
    
    @staticmethod
    def to_dict(process):
        """Convert database row to dictionary"""
        return {
            'process_id': process['process_id'],
            'run_id': process['run_id'],
            'name': process['name'],
            'arrival_time': process['arrival_time'],
            'burst_time': process['burst_time'],
            'priority': process['priority'],
            'state': process['state'],
            'completion_time': process['completion_time'],
            'turnaround_time': process['turnaround_time'],
            'waiting_time': process['waiting_time']
        }
