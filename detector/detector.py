import time
from collections import Counter

from detector.state import (
    global_window,
    ip_request_counter,
    banned_ips,
    state_lock,
    add_alert,
    add_audit,
)
from detector.notifier import send_slack_alert
from detector.blocker import block_ip


THRESHOLD_MULTIPLIER = 3

def start_detector_loop():
    while True:
        time.sleep(10)

        with state_lock:
            global_rate = len(global_window)
            ip_stats = dict(ip_request_counter)

        if global_rate == 0:
            continue

        suspicious = [
            (ip, count)
            for ip, count in ip_stats.items()
            if count > THRESHOLD_MULTIPLIER
        ]

        if not suspicious:
            continue

        suspicious.sort(key=lambda x: x[1], reverse=True)
        top_ip, top_count = suspicious[0]

        if top_ip in banned_ips:
            continue

        block_ip(top_ip)

        banned_ips[top_ip] = {
            "time": time.time(),
            "count": top_count,
            "global_rate": global_rate,
        }

        attack_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ip": top_ip,
            "count": top_count,
            "global_rate": global_rate,
        }

        add_alert(str(attack_data))
        add_audit(f"Attack detected: {attack_data}")

        message = (
            f"Rate: {global_rate}\n"
            f"IP: {top_ip}\n"
            f"Count: {top_count}"
        )

        send_slack_alert("🚨 Anomaly Detected", message)
