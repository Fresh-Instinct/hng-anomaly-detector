# notifier.py
import yaml
import requests
from datetime import datetime
from state import add_alert, add_audit

with open("detector/config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

WEBHOOK = cfg.get("slack_webhook", "")


def send_slack_alert(title, body):
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    message = f"*{title}*
{body}
Time: {timestamp}"

    add_alert(message)
    add_audit(f"[{timestamp}] ALERT system | {title} | {body.replace(chr(10), ' | ')}")

    if not WEBHOOK:
        print("[!] Slack webhook not configured")
        return

    try:
        requests.post(WEBHOOK, json={"text": message}, timeout=5)
    except Exception as e:
        print(f"[!] Slack notification failed: {e}")
