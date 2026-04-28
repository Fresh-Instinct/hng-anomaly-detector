import os
import time
from datetime import datetime
from state import banned_ips, state_lock, add_audit
from notifier import send_slack_alert


def start_unbanner():
    while True:
        now = time.time()
        expired = []

        with state_lock:
            for ip, meta in list(banned_ips.items()):
                if meta['ban_until'] and now >= meta['ban_until']:
                    expired.append((ip, meta))

            for ip, meta in expired:
                try:
                    os.system(f"iptables -D INPUT -s {ip} -j DROP")
                except:
                    pass

                del banned_ips[ip]

                ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                event = f"[{ts}] UNBAN {ip} | timeout expired | - | - | released"
                add_audit(event)

                send_slack_alert(
                    "✅ IP UNBANNED",
                    f"IP: {ip}
Previous Duration: {meta['duration']}
Reason: Ban timer expired"
                )

        time.sleep(5)
