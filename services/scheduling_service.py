class SchedulingService:
    def run_algorithm(self, algorithm, processes, time_quantum=2):
        """Run the specified scheduling algorithm"""
        if algorithm == 'fcfs':
            return self.fcfs(processes)
        elif algorithm == 'sjf':
            return self.sjf(processes)
        elif algorithm == 'srtf':
            return self.srtf(processes)
        elif algorithm == 'round_robin':
            return self.round_robin(processes, time_quantum)
        elif algorithm == 'priority':
            return self.priority(processes)
        else:
            return self.fcfs(processes)
    
    def fcfs(self, processes):
        """First-Come, First-Served"""
        sorted_processes = sorted(processes, key=lambda p: p.arrival_time)
        current_time = 0
        
        for p in sorted_processes:
            if current_time < p.arrival_time:
                current_time = p.arrival_time
            p.completion_time = current_time + p.burst_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            current_time = p.completion_time
        
        return {
            'algorithm': 'FCFS',
            'processes': [p.to_dict() for p in sorted_processes],
            'gantt_chart': self.build_gantt(sorted_processes)
        }
    
    def sjf(self, processes):
        """Shortest Job First (non-preemptive)"""
        sorted_processes = sorted(processes, key=lambda p: (p.arrival_time, p.burst_time))
        current_time = 0
        completed = []
        remaining = sorted_processes.copy()
        
        while remaining:
            available = [p for p in remaining if p.arrival_time <= current_time]
            if available:
                shortest = min(available, key=lambda p: p.burst_time)
                p = shortest
                remaining.remove(p)
                p.completion_time = current_time + p.burst_time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                current_time = p.completion_time
                completed.append(p)
            else:
                current_time += 1
        
        return {
            'algorithm': 'SJF',
            'processes': [p.to_dict() for p in completed],
            'gantt_chart': self.build_gantt(completed)
        }
    
    def srtf(self, processes):
        """Shortest Remaining Time First (preemptive)"""
        # Simplified SRTF implementation
        current_time = 0
        completed = []
        remaining = [{'p': p, 'remaining': p.burst_time} for p in processes]
        
        while remaining:
            available = [r for r in remaining if r['p'].arrival_time <= current_time]
            if available:
                shortest = min(available, key=lambda r: r['remaining'])
                r = shortest
                r['remaining'] -= 1
                current_time += 1
                if r['remaining'] == 0:
                    p = r['p']
                    p.completion_time = current_time
                    p.turnaround_time = p.completion_time - p.arrival_time
                    p.waiting_time = p.turnaround_time - p.burst_time
                    remaining.remove(r)
                    completed.append(p)
            else:
                current_time += 1
        
        return {
            'algorithm': 'SRTF',
            'processes': [p.to_dict() for p in completed],
            'gantt_chart': self.build_gantt(completed)
        }
    
    def round_robin(self, processes, time_quantum):
        """Round Robin"""
        queue = sorted(processes, key=lambda p: p.arrival_time)
        current_time = 0
        remaining = {p.process_id: p.burst_time for p in processes}
        completed = []
        gantt = []
        
        while queue:
            p = queue.pop(0)
            if current_time < p.arrival_time:
                current_time = p.arrival_time
            
            exec_time = min(time_quantum, remaining[p.process_id])
            gantt.append({'process': p.name, 'start': current_time, 'duration': exec_time})
            current_time += exec_time
            remaining[p.process_id] -= exec_time
            
            if remaining[p.process_id] == 0:
                p.completion_time = current_time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                completed.append(p)
            else:
                queue.append(p)
        
        return {
            'algorithm': 'Round Robin',
            'processes': [p.to_dict() for p in completed],
            'gantt_chart': gantt
        }
    
    def priority(self, processes):
        """Priority Scheduling (non-preemptive)"""
        sorted_processes = sorted(processes, key=lambda p: (p.arrival_time, p.priority))
        current_time = 0
        completed = []
        remaining = sorted_processes.copy()
        
        while remaining:
            available = [p for p in remaining if p.arrival_time <= current_time]
            if available:
                highest = min(available, key=lambda p: p.priority)
                p = highest
                remaining.remove(p)
                p.completion_time = current_time + p.burst_time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                current_time = p.completion_time
                completed.append(p)
            else:
                current_time += 1
        
        return {
            'algorithm': 'Priority',
            'processes': [p.to_dict() for p in completed],
            'gantt_chart': self.build_gantt(completed)
        }
    
    def build_gantt(self, processes):
        """Build Gantt chart data"""
        gantt = []
        current_time = 0
        for p in processes:
            if current_time < p.arrival_time:
                current_time = p.arrival_time
            gantt.append({
                'process': p.name,
                'start': current_time,
                'duration': p.burst_time
            })
            current_time += p.burst_time
        return gantt
