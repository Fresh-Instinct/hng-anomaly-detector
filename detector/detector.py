# detector.py
from collections import defaultdict, deque
from typing import Dict, Tuple, Optional
import time

class AnomalyDetector:
    def __init__(self, short_window: int = 60, z_threshold: float = 3.0, multiplier: float = 5.0):
        """Initialize anomaly detector with sliding windows"""
        self.short_window = short_window
        self.z_threshold = z_threshold
        self.multiplier = multiplier
        
        # Sliding windows (60 seconds)
        self.ip_rates = defaultdict(lambda: deque(maxlen=short_window))      # Per-IP rates
        self.global_rate = deque(maxlen=short_window))                       # Global rate
        self.ip_errors = defaultdict(lambda: deque(maxlen=short_window))     # Per-IP errors
        
        # Dynamic thresholds (error surge)
        self.tightened_ips = {}
        self.error_baseline = 0.01  # Global error baseline
    
    def get_rate(self, window: deque) -> float:
        """Calculate rate from sliding window (req/s)"""
        if not window:
            return 0.0
        total_requests = sum(count for _, count in window)
        return total_requests / len(window)
    
    def update_rate(self, ip: str, status: int, timestamp: float):
        """Update all sliding windows"""
        current_second = int(timestamp)
        
        # GLOBAL rate (1st window requirement)
        if not self.global_rate or current_second != self.global_rate[-1][0]:
            self.global_rate.append([current_second, 1])
        else:
            self.global_rate[-1][1] += 1
        
        # PER-IP rate (2nd window requirement)
        if not self.ip_rates[ip] or current_second != self.ip_rates[ip][-1][0]:
            self.ip_rates[ip].append([current_second, 1])
        else:
            self.ip_rates[ip][-1][1] += 1
        
        # ERROR tracking (4xx/5xx)
        if status >= 400:
            if not self.ip_errors[ip] or current_second != self.ip_errors[ip][-1][0]:
                self.ip_errors[ip].append([current_second, 1])
            else:
                self.ip_errors[ip][-1][1] += 1
    
    def is_anomalous_ip(self, ip: str, baseline_mean: float, baseline_std: float) -> Tuple[bool, str]:
        """Detect IP anomaly - Z-SCORE 3.0 OR 5x MULTIPLIER (whichever fires first)"""
        rate = self.get_rate(self.ip_rates[ip])
        error_rate = self.get_rate(self.ip_errors[ip])
        
        # ERROR SURGE: Tighten thresholds if 3x baseline errors
        if error_rate > self.error_baseline * 3:
            self.tightened_ips[ip] = True
            z_thresh = self.z_threshold * 0.7  # Tighten 30%
            mult_thresh = self.multiplier * 0.7
        else:
            z_thresh, mult_thresh = self.z_threshold, self.multiplier
        
        # Z-SCORE DETECTION (fires first if > 3.0)
        if baseline_std > 0:
            z_score = (rate - baseline_mean) / baseline_std
            if z_score > z_thresh:
                return True, f"z-score={z_score:.2f}"
        
        # MULTIPLIER DETECTION (fires first if > 5x)
        if rate > baseline_mean * mult_thresh:
            return True, f"{rate/baseline_mean:.1f}x baseline"
        
        return False, ""
    
    def is_global_anomalous(self, baseline_mean: float, baseline_std: float) -> Tuple[bool, str]:
        """Global anomaly detection (same logic)"""
        rate = self.get_rate(self.global_rate)
        
        # Z-Score first
        if baseline_std > 0:
            z_score = (rate - baseline_mean) / baseline_std
            if z_score > self.z_threshold:
                return True, f"global z-score={z_score:.2f}"
        
        # Multiplier second
        if rate > baseline_mean * self.multiplier:
            return True, f"global {rate/baseline_mean:.1f}x baseline"
        
        return False, ""
    
    def get_top_ips(self, limit: int = 10) -> Dict[str, float]:
        """Top 10 IPs by rate for dashboard"""
        rates = {ip: self.get_rate(window) for ip, window in self.ip_rates.items()}
        return dict(sorted(rates.items(), key=lambda x: x[1], reverse=True)[:limit])
