import time
import json
from datetime import datetime

from state import (
    global_window,
    ip_windows,
    ip_error_windows,
    ip_request_counter,
    state_lock,
)
from detector import start_detector_loop  # optional if needed in architecture

NGINX_LOG_PATH = "nginx/logs/access.log"


def parse_log_line(line):
    """Parse JSON nginx log line"""
    try:
        return json.loads(line)
    except:
        return None


def start_log_monitor():
    """Continuously monitor nginx logs and populate sliding windows"""

    print("[+] Log monitor started...")

    # open file and move to end (like tail -f)
    with open(NGINX_LOG_PATH, "r") as f:
        f.seek(0, 2)

        while True:
            line = f.readline()

            if not line:
                time.sleep(0.1)
                continue

            data = parse_log_line(line.strip())
            if not data:
                continue

            ip = data.get("source_ip")
            ts_str = data.get("timestamp")
            status = int(data.get("status", 200))

            try:
                # convert timestamp to epoch (approx safe fallback)
                now = time.time()
            except:
                now = time.time()

            with state_lock:
                # GLOBAL WINDOW
                global_window.append(now)

                # PER IP WINDOW
                ip_windows[ip].append(now)

                # REQUEST COUNTER
                ip_request_counter[ip] += 1

                # ERROR TRACKING
                if status >= 400:
                    ip_error_windows[ip].append(now)

                # CLEAN OLD ENTRIES (60s sliding window)
                cutoff = now - 60
                    edq
