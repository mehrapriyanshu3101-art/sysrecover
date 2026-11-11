import psutil
import random
from datetime import datetime

class SystemProcessService:
    """Service to fetch real system processes from Windows Task Manager"""
    
    def get_system_processes(self, limit=20):
        """Fetch real system processes and convert to simulation format"""
        processes = []
        
        try:
            # Get all running processes
            system_processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']))
            
            # Sort by CPU usage to get most relevant processes
            system_processes.sort(key=lambda x: x.info['cpu_percent'] or 0, reverse=True)
            
            # Take top processes
            top_processes = system_processes[:limit]
            
            for i, proc in enumerate(top_processes):
                try:
                    name = proc.info['name'] or f'Process_{proc.info["pid"]}'
                    
                    # Map system metrics to simulation parameters
                    # CPU percent -> burst time (scaled)
                    burst_time = max(1, int((proc.info['cpu_percent'] or 1) * 2))
                    
                    # Memory percent -> priority (higher memory = higher priority)
                    priority = int((proc.info['memory_percent'] or 0) * 10)
                    
                    # Process creation time -> arrival time (relative to current time)
                    create_time = proc.info['create_time'] or datetime.now().timestamp()
                    arrival_time = max(0, int((datetime.now().timestamp() - create_time) / 60))  # minutes
                    
                    processes.append({
                        'name': name[:50],  # Limit name length
                        'arrival_time': min(arrival_time, 100),  # Cap at reasonable value
                        'burst_time': min(burst_time, 50),  # Cap at reasonable value
                        'priority': min(priority, 10)  # Cap at reasonable value
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # If we couldn't get enough processes, add some fallback ones
            if len(processes) < 5:
                fallback_processes = [
                    {'name': 'System', 'arrival_time': 0, 'burst_time': 5, 'priority': 1},
                    {'name': 'svchost', 'arrival_time': 1, 'burst_time': 8, 'priority': 2},
                    {'name': 'explorer', 'arrival_time': 2, 'burst_time': 10, 'priority': 3},
                    {'name': 'chrome', 'arrival_time': 3, 'burst_time': 15, 'priority': 4},
                    {'name': 'python', 'arrival_time': 4, 'burst_time': 12, 'priority': 5},
                ]
                processes.extend(fallback_processes[:5 - len(processes)])
            
        except Exception as e:
            # Fallback to mock data if system process retrieval fails
            processes = [
                {'name': 'System', 'arrival_time': 0, 'burst_time': 5, 'priority': 1},
                {'name': 'svchost', 'arrival_time': 1, 'burst_time': 8, 'priority': 2},
                {'name': 'explorer', 'arrival_time': 2, 'burst_time': 10, 'priority': 3},
                {'name': 'chrome', 'arrival_time': 3, 'burst_time': 15, 'priority': 4},
                {'name': 'python', 'arrival_time': 4, 'burst_time': 12, 'priority': 5},
            ]
        
        return processes
