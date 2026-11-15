import math
import time

import psutil


FALLBACK_PROCESSES = [
    {'name': 'System', 'arrival_time': 0, 'burst_time': 5, 'priority': 1},
    {'name': 'svchost', 'arrival_time': 1, 'burst_time': 8, 'priority': 2},
    {'name': 'explorer', 'arrival_time': 2, 'burst_time': 10, 'priority': 3},
    {'name': 'chrome', 'arrival_time': 3, 'burst_time': 15, 'priority': 4},
    {'name': 'python', 'arrival_time': 4, 'burst_time': 12, 'priority': 5},
]


class SystemProcessService:
    """Service to fetch real system processes from Windows Task Manager"""

    def get_system_processes(self, limit=20):
        """Fetch real system processes and convert to simulation format"""
        processes = []

        try:
            system_processes = list(psutil.process_iter(
                ['pid', 'name', 'cpu_times', 'memory_percent', 'create_time']
            ))

            # psutil reports 0% CPU unless the counters are sampled over an interval
            for proc in system_processes:
                try:
                    proc.cpu_percent(None)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            time.sleep(0.3)

            now = time.time()
            samples = []

            for proc in system_processes:
                try:
                    info = proc.info
                    cpu_times = info['cpu_times']
                    cpu_seconds = (cpu_times.user + cpu_times.system) if cpu_times else 0.0

                    samples.append({
                        'pid': info['pid'],
                        'name': (info['name'] or f"Process_{info['pid']}")[:50],
                        'cpu_percent': proc.cpu_percent(None) or 0.0,
                        'cpu_seconds': cpu_seconds,
                        'memory_percent': info['memory_percent'] or 0.0,
                        'uptime_minutes': max(0.0, now - (info['create_time'] or now)) / 60,
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            # Take the busiest processes
            samples.sort(key=lambda s: (s['cpu_percent'], s['cpu_seconds']), reverse=True)
            samples = samples[:limit]

            if samples:
                count = len(samples)

                # Spread arrivals over 0..24 so processes do not all arrive at once
                by_uptime = sorted(samples, key=lambda s: s['uptime_minutes'], reverse=True)
                for rank, sample in enumerate(by_uptime):
                    sample['arrival_time'] = round(rank * 24 / max(1, count - 1))

                # Spread priorities over 0..9 (0 = highest priority, most memory)
                by_memory = sorted(samples, key=lambda s: s['memory_percent'], reverse=True)
                for rank, sample in enumerate(by_memory):
                    sample['priority'] = round(rank * 9 / max(1, count - 1))

                for sample in samples:
                    # Current CPU usage plus how much CPU the process has used overall
                    burst = round(sample['cpu_percent']) + int(math.log2(1 + sample['cpu_seconds']))
                    processes.append({
                        'name': sample['name'],
                        'arrival_time': sample['arrival_time'],
                        'burst_time': max(1, min(20, burst)),
                        'priority': sample['priority']
                    })

            # If we couldn't get enough processes, add some fallback ones
            if len(processes) < 5:
                processes.extend(FALLBACK_PROCESSES[:5 - len(processes)])

        except Exception:
            # Fallback to mock data if system process retrieval fails
            processes = list(FALLBACK_PROCESSES)

        return processes
