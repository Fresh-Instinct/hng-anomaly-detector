import os
import time
from datetime import datetime

from detector.state import banned_ips, state_lock, add_audit
from detector.notifier import send_slack_alert


def start_unbanner():
    while True:
        time.sleep(20)

        expired = []

        with state_lock:
            now = time.time()

            for ip, info in list(banned_ips.items()):
                ban_until = info.get("ban_until")

                if ban_until is not None and now >= ban_until:
                    expired.append((ip, info))

        for ip, info in expired:
            try:
                os.system(f"iptables -D INPUT -s {ip} -j DROP")
            except:
                pass

            with state_lock:
                if ip in banned_ips:
                    del banned_ips[ip]

            ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            duration = info.get("duration", "temporary")

            add_audit(f"[{ts}] UNBAN {ip} | duration_served={duration}")

            send_slack_alert(
                "♻️ IP UNBANNED",
                f"IP: {ip}\nDuration Served: {duration}\nStatus: Restored"
            )
