# baseline.py
class BaselineCalculator:
    def __init__(self, window=1800):  # 👈 30min
        self.per_second_counts = deque(maxlen=1800)
        self.hourly_baselines = {}  # 👈 24 slots
    
    def recalculate(self):
        counts = list(self.per_second_counts)
        mean = sum(counts) / len(counts)
        stddev = (sum((x-mean)**2 for x in counts) / len(counts))**0.5
        return max(mean, 0.1), max(stddev, 0.1)  # 👈 Floor values
