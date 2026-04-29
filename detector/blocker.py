import os
import time
from datetime import datetime

from detector.state import banned_ips, state_lock, add_audit
from detector.notifier import send_slack_alert

BAN_SCHEDULE = {
    1: (600, "10 minutes"),
    2: (1800, "30 minutes"),
    3: (7200, "2 hours"),
    4: (None, "PERMANENT")
}


def block_ip(ip, condition, rate, baseline):
    with state_lock:
        if ip in banned_ips:
            return

        strikes = banned_ips.get(ip, {}).get("strikes", 0) + 1
        strikes = min(strikes, 4)

        seconds, duration = BAN_SCHEDULE[strikes]
        ban_until = None if seconds is None else time.time() + seconds

        os.system(f"iptables -I INPUT -s {ip} -j DROP")

        banned_ips[ip] = {
            "strikes": strikes,
            "ban_until": ban_until,
            "duration": duration,
            "condition": condition
        }

    ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    event = f"[{ts}] BAN {ip} | {condition} | {rate} | {baseline} | {duration}"
    add_audit(event)

    message = (
        f"🚫 IP BANNED\n"
        f"IP: {ip}\n"
        f"Condition: {condition}\n"
        f"Rate: {rate}\n"
        f"Baseline: {baseline}\n"
        f"Duration: {duration}"
    )

    send_slack_alert(message, "IP BANNED")
