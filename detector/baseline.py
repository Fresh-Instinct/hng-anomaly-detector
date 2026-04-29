import time
import statistics
import detector.state

from datetime import datetime
from detector.state import (
    global_window,
    ip_error_windows,
    hourly_history,
    state_lock,
    add_audit,
)


def start_baseline_scheduler():
    while True:
        time.sleep(60)
        now = time.time()
        hour_slot = time.strftime('%H')

        with state_lock:
            # current global req count in last 60 sec
            current_count = len(global_window)
            hourly_history[hour_slot].append(current_count)

            samples = hourly_history[hour_slot]
            if len(samples) >= 5:
                state.baseline_mean = max(statistics.mean(samples), 1.0)
                state.baseline_stddev = max(statistics.stdev(samples), 1.0) if len(samples) > 1 else 1.0
            else:
                state.baseline_mean = 1.0
                state.baseline_stddev = 1.0

            # calculate error baseline
            total_errors = sum(len(v) for v in ip_error_windows.values())
            state.baseline_error_mean = max(total_errors / max(len(ip_error_windows), 1), 0.1)
            state.current_hour_slot = hour_slot

            ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
            add_audit(
                f"[{ts}] BASELINE RECALC system | hourly_slot={hour_slot} | mean={state.baseline_mean:.2f} | std={state.baseline_stddev:.2f}"
            )
