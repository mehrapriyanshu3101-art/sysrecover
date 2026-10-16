class MemoryService:
    def run_simulation(self, reference_string, num_frames, algorithm):
        """Run the specified page replacement algorithm"""
        if algorithm == 'fifo':
            return self.fifo(reference_string, num_frames)
        elif algorithm == 'lru':
            return self.lru(reference_string, num_frames)
        elif algorithm == 'optimal':
            return self.optimal(reference_string, num_frames)
        else:
            return self.fifo(reference_string, num_frames)
    
    def fifo(self, reference_string, num_frames):
        """First-In, First-Out page replacement"""
        frames = []
        page_faults = 0
        steps = []
        
        for i, page in enumerate(reference_string):
            if page in frames:
                steps.append({
                    'step': i,
                    'page': page,
                    'frames': frames.copy(),
                    'fault': False
                })
            else:
                page_faults += 1
                if len(frames) < num_frames:
                    frames.append(page)
                else:
                    frames.pop(0)
                    frames.append(page)
                steps.append({
                    'step': i,
                    'page': page,
                    'frames': frames.copy(),
                    'fault': True
                })
        
        return {
            'algorithm': 'FIFO',
            'page_faults': page_faults,
            'hit_ratio': (len(reference_string) - page_faults) / len(reference_string),
            'steps': steps
        }
    
    def lru(self, reference_string, num_frames):
        """Least Recently Used page replacement"""
        frames = []
        last_used = {}
        page_faults = 0
        steps = []
        
        for i, page in enumerate(reference_string):
            if page in frames:
                last_used[page] = i
                steps.append({
                    'step': i,
                    'page': page,
                    'frames': frames.copy(),
                    'fault': False
                })
            else:
                page_faults += 1
                if len(frames) < num_frames:
                    frames.append(page)
                else:
                    lru_page = min(frames, key=lambda p: last_used[p])
                    frames[frames.index(lru_page)] = page
                last_used[page] = i
                steps.append({
                    'step': i,
                    'page': page,
                    'frames': frames.copy(),
                    'fault': True
                })
        
        return {
            'algorithm': 'LRU',
            'page_faults': page_faults,
            'hit_ratio': (len(reference_string) - page_faults) / len(reference_string),
            'steps': steps
        }
    
    def optimal(self, reference_string, num_frames):
        """Optimal page replacement (knows future)"""
        frames = []
        page_faults = 0
        steps = []
        
        for i, page in enumerate(reference_string):
            if page in frames:
                steps.append({
                    'step': i,
                    'page': page,
                    'frames': frames.copy(),
                    'fault': False
                })
            else:
                page_faults += 1
                if len(frames) < num_frames:
                    frames.append(page)
                else:
                    # Find page that won't be used for longest time
                    future_use = {}
                    for f in frames:
                        if f in reference_string[i+1:]:
                            future_use[f] = reference_string[i+1:].index(f)
                        else:
                            future_use[f] = float('inf')
                    replace_page = max(frames, key=lambda p: future_use[p])
                    frames[frames.index(replace_page)] = page
                steps.append({
                    'step': i,
                    'page': page,
                    'frames': frames.copy(),
                    'fault': True
                })
        
        return {
            'algorithm': 'Optimal',
            'page_faults': page_faults,
            'hit_ratio': (len(reference_string) - page_faults) / len(reference_string),
            'steps': steps
        }
