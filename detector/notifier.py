# notifier.py
import yaml
import requests
from datetime import datetime
from detector.state import add_alert, add_audit

with open("detector/config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

WEBHOOK = cfg.get("slack_webhook", "")


def send_slack_alert(message: str, title: str = "ALERT"):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    formatted = f"*{title}*\n{message}\nTime: {timestamp}"

    # internal logging
    add_alert(formatted)
    add_audit(f"[{timestamp}] ALERT system | {title} | {message.replace(chr(10), ' | ')}")

    # slack
    if not WEBHOOK:
        print("[!] Slack webhook not configured")
        return

    try:
        requests.post(WEBHOOK, json={"text": formatted}, timeout=5)
    except Exception as e:
        print(f"[!] Slack notification failed: {e}")
