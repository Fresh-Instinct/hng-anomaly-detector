import time
from threading import Thread

from monitor import start_log_monitor
from detector import start_detector_loop
from baseline import start_baseline_scheduler
from unbanner import start_unbanner
from dashboard import start_dashboard


def start_thread(target, name):
    print(f"[+] Starting {name}...")
    t = Thread(target=target, daemon=True)
    t.start()
    return t


if __name__ == "__main__":
    print("======================================")
    print(" HNG ANOMALY DETECTOR STARTING ")
    print("======================================")

    start_thread(start_log_monitor, "Log Monitor")
    start_thread(start_detector_loop, "Detector Engine")
    start_thread(start_baseline_scheduler, "Baseline Scheduler")
    start_thread(start_unbanner, "Unbanner")
    start_thread(start_dashboard, "Dashboard")

    print("[+] System fully operational.")

    while True:
        time.sleep(5)
