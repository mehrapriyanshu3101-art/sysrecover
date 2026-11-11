import psutil

class SystemResourceService:
    """Service to fetch real system resources from Windows"""
    
    def get_system_resources(self):
        """Fetch real system resources and convert to simulation format"""
        resources = []
        
        try:
            # CPU as a resource
            cpu_count = psutil.cpu_count(logical=True)
            resources.append({
                'resource_name': 'CPU',
                'resource_type': 'processor',
                'total_instances': cpu_count,
                'available_instances': cpu_count
            })
            
            # Memory as a resource
            mem = psutil.virtual_memory()
            # Convert to GB chunks (each chunk is 1GB)
            total_gb = int(mem.total / (1024**3))
            available_gb = int(mem.available / (1024**3))
            resources.append({
                'resource_name': 'RAM',
                'resource_type': 'memory',
                'total_instances': total_gb,
                'available_instances': available_gb
            })
            
            # Disk I/O as a resource
            disk_partitions = psutil.disk_partitions()
            for partition in disk_partitions:
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    resources.append({
                        'resource_name': f'Disk_{partition.device.replace(":", "")}',
                        'resource_type': 'io',
                        'total_instances': 1,
                        'available_instances': 1
                    })
                except:
                    continue
            
            # Network as a resource
            resources.append({
                'resource_name': 'Network',
                'resource_type': 'io',
                'total_instances': 1,
                'available_instances': 1
            })
            
            # GPU (if available)
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    resources.append({
                        'resource_name': f'GPU_{gpu.id}',
                        'resource_type': 'io',
                        'total_instances': 1,
                        'available_instances': 1
                    })
            except ImportError:
                # GPUtil not available, skip GPU
                pass
            
        except Exception as e:
            # Fallback to basic resources
            resources = [
                {'resource_name': 'CPU', 'resource_type': 'processor', 'total_instances': 4, 'available_instances': 4},
                {'resource_name': 'RAM', 'resource_type': 'memory', 'total_instances': 8, 'available_instances': 8},
                {'resource_name': 'Disk', 'resource_type': 'io', 'total_instances': 1, 'available_instances': 1},
                {'resource_name': 'Network', 'resource_type': 'io', 'total_instances': 1, 'available_instances': 1}
            ]
        
        return resources
