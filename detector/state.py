import time
from collections import deque, defaultdict
from threading import Lock

# ===== Runtime Locks =====
state_lock = Lock()

# ===== Sliding Windows =====
# Global request timestamps for last 60 seconds
global_window = deque()

# Per-IP request timestamps for last 60 seconds
ip_windows = defaultdict(deque)

# ===== Compatibility layer (fix broken imports) =====
request_timestamps = global_window

# Per-IP error timestamps (4xx/5xx) for last 60 seconds
ip_error_windows = defaultdict(deque)

# ===== Rolling Baseline History =====
# Keep 30 mins of per-second counts per hour slot
hourly_history = defaultdict(lambda: deque(maxlen=1800))

# Effective baseline values
baseline_mean = 1.0
baseline_stddev = 1.0
baseline_error_mean = 0.1
current_hour_slot = time.strftime('%H')

# ===== Ban Tracking =====
# banned_ips[ip] = {
#   strikes: int,
#   ban_until: epoch or None,
#   duration: str,
#   condition: str
# }
banned_ips = {}

# ===== Top IP Counters =====
ip_request_counter = defaultdict(int)

# ===== Recent Alerts / Audit =====
recent_alerts = deque(maxlen=50)
audit_events = deque(maxlen=200)

# ===== Service Uptime =====
start_time = time.time()

# ===== Helper Functions =====
def add_audit(event: str):
    with state_lock:
        audit_events.append(event)


def add_alert(event: str):
    with state_lock:
        recent_alerts.append(event)
