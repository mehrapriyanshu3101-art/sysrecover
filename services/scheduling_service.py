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
        sorted_processes = sorted(processes, key=lambda p: (p.arrival_time, p.process_id))
        current_time = 0
        blocks = []

        for p in sorted_processes:
            if current_time < p.arrival_time:
                current_time = p.arrival_time
            start = current_time
            p.completion_time = start + p.burst_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            current_time = p.completion_time
            blocks.append(self.make_block(p.name, start, p.completion_time))

        return {
            'algorithm': 'FCFS',
            'processes': [p.to_dict() for p in sorted_processes],
            'gantt_chart': blocks
        }

    def sjf(self, processes):
        """Shortest Job First (non-preemptive)"""
        current_time = 0
        completed = []
        remaining = sorted(processes, key=lambda p: (p.arrival_time, p.process_id))
        blocks = []

        while remaining:
            available = [p for p in remaining if p.arrival_time <= current_time]

            if not available:
                current_time = min(p.arrival_time for p in remaining)
                continue

            p = min(available, key=lambda proc: (proc.burst_time, proc.arrival_time, proc.process_id))
            remaining.remove(p)

            start = current_time
            p.completion_time = start + p.burst_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            current_time = p.completion_time

            blocks.append(self.make_block(p.name, start, p.completion_time))
            completed.append(p)

        return {
            'algorithm': 'SJF',
            'processes': [p.to_dict() for p in completed],
            'gantt_chart': blocks
        }

    def srtf(self, processes):
        """Shortest Remaining Time First (preemptive)"""
        current_time = 0
        completed = []
        blocks = []
        remaining = {p.process_id: p.burst_time for p in processes}

        while any(time_left > 0 for time_left in remaining.values()):
            available = [
                p for p in processes
                if p.arrival_time <= current_time and remaining[p.process_id] > 0
            ]

            if not available:
                current_time = min(
                    p.arrival_time for p in processes if remaining[p.process_id] > 0
                )
                continue

            p = min(available, key=lambda proc: (remaining[proc.process_id], proc.arrival_time, proc.process_id))

            # Run this process for one time unit, merging consecutive slices
            self.append_slice(blocks, p.name, current_time, current_time + 1)
            remaining[p.process_id] -= 1
            current_time += 1

            if remaining[p.process_id] == 0:
                p.completion_time = current_time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                completed.append(p)

        return {
            'algorithm': 'SRTF',
            'processes': [p.to_dict() for p in completed],
            'gantt_chart': blocks
        }

    def round_robin(self, processes, time_quantum):
        """Round Robin"""
        if time_quantum < 1:
            time_quantum = 1

        queue = []
        not_arrived = sorted(processes, key=lambda p: (p.arrival_time, p.process_id))
        current_time = 0
        remaining = {p.process_id: p.burst_time for p in processes}
        completed = []
        blocks = []

        while queue or not_arrived:
            # Admit processes that have arrived by now
            for proc in [p for p in not_arrived if p.arrival_time <= current_time]:
                not_arrived.remove(proc)
                queue.append(proc)

            if not queue:
                current_time = min(p.arrival_time for p in not_arrived)
                continue

            p = queue.pop(0)

            exec_time = min(time_quantum, remaining[p.process_id])
            self.append_slice(blocks, p.name, current_time, current_time + exec_time)
            current_time += exec_time
            remaining[p.process_id] -= exec_time

            # Processes that arrived during this slice join before the current one is re-queued
            for proc in [q for q in not_arrived if q.arrival_time <= current_time]:
                not_arrived.remove(proc)
                queue.append(proc)

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
            'gantt_chart': blocks
        }

    def priority(self, processes):
        """Priority Scheduling (non-preemptive, lower number = higher priority)"""
        current_time = 0
        completed = []
        remaining = sorted(processes, key=lambda p: (p.arrival_time, p.process_id))
        blocks = []

        while remaining:
            available = [p for p in remaining if p.arrival_time <= current_time]

            if not available:
                current_time = min(p.arrival_time for p in remaining)
                continue

            p = min(available, key=lambda proc: (proc.priority, proc.arrival_time, proc.process_id))
            remaining.remove(p)

            start = current_time
            p.completion_time = start + p.burst_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            current_time = p.completion_time

            blocks.append(self.make_block(p.name, start, p.completion_time))
            completed.append(p)

        return {
            'algorithm': 'Priority',
            'processes': [p.to_dict() for p in completed],
            'gantt_chart': blocks
        }

    @staticmethod
    def make_block(name, start, end):
        """A single execution block for the Gantt chart"""
        return {'process': name, 'start': start, 'end': end, 'duration': end - start}

    @staticmethod
    def append_slice(blocks, name, start, end):
        """Merge a slice into the previous block when the same process keeps running"""
        if blocks and blocks[-1]['process'] == name and blocks[-1]['end'] == start:
            blocks[-1]['end'] = end
            blocks[-1]['duration'] = end - blocks[-1]['start']
        else:
            blocks.append({'process': name, 'start': start, 'end': end, 'duration': end - start})
