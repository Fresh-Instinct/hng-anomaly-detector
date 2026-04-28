import time
import statistics
from datetime import datetime

import state
from state import (
    global_window,
    ip_windows,
    ip_error_windows,
    banned_ips,
    state_lock,
    add_audit,
    baseline_mean,
    baseline_stddev,
)
from blocker import ban_ip
from notifier import send_slack_alert

Z_THRESHOLD = 3.0
MULTIPLIER = 5


def start_detector_loop():
    """Main anomaly detection engine (runs continuously)"""
    while True:
        time.sleep(1)
        now = time.time()

        with state_lock:
            # ================= GLOBAL TRAFFIC =================
            global_rate = len(global_window)

            # z-score calculation
            std = state.baseline_stddev if state.baseline_stddev > 0 else 1
            z_score = (global_rate - state.baseline_mean) / std

            global_anomaly = (
                z_score > Z_THRESHOLD
                or global_rate > state.baseline_mean * MULTIPLIER
            )

            if global_anomaly:
                ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                event = f"[{ts}] GLOBAL ALERT | z={z_score:.2f} | rate={global_rate} | mean={state.baseline_mean:.2f}"
                add_audit(event)

                send_slack_alert(
                    "🌍 GLOBAL TRAFFIC ANOMALY",
                    f"Rate: {global_rate}
Baseline: {state.baseline_mean:.2f}
Z-score: {z_score:.2f}"
                )

            # ================= PER-IP DETECTION =================
            for ip, dq in list(ip_windows.items()):
                if ip in banned_ips:
                    continue
                global_window.popleft()
