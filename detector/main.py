#!/usr/bin/env python3
import time
from flask import Flask
from datetime import datetime
from collections import deque

app = Flask(__name__)

start_time = time.time()
global_rate = deque(maxlen=60)
banned_ips = set()
audit_log = []

def log_audit(action, ip='', condition='', rate=0, baseline=0):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = f'[{ts}] {action}
