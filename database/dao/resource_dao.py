from database.mysql_connection import db

class ResourceDAO:
    """Data Access Object for Resource table"""
    
    @staticmethod
    def get_by_run_id(run_id):
        """Get all resources for a simulation run"""
        query = "SELECT * FROM resource WHERE run_id = %s ORDER BY resource_id"
        return db.execute_query(query, (run_id,))
    
    @staticmethod
    def get_by_id(resource_id):
        """Get resource by ID"""
        query = "SELECT * FROM resource WHERE resource_id = %s"
        result = db.execute_query(query, (resource_id,))
        return result[0] if result else None
    
    @staticmethod
    def create(run_id, resource_name, resource_type, total_instances):
        """Create a new resource"""
        query = """
            INSERT INTO resource (run_id, resource_name, resource_type, total_instances, available_instances)
            VALUES (%s, %s, %s, %s, %s)
        """
        resource_id = db.execute_query(query, (run_id, resource_name, resource_type, total_instances, total_instances), fetch=False)
        return ResourceDAO.get_by_id(resource_id)
    
    @staticmethod
    def delete(resource_id):
        """Delete a resource"""
        query = "DELETE FROM resource WHERE resource_id = %s"
        db.execute_query(query, (resource_id,), fetch=False)
    
    @staticmethod
    def to_dict(resource):
        """Convert database row to dictionary"""
        return {
            'resource_id': resource['resource_id'],
            'run_id': resource['run_id'],
            'resource_name': resource['resource_name'],
            'resource_type': resource['resource_type'],
            'total_instances': resource['total_instances'],
            'available_instances': resource['available_instances']
        }
