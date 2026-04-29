from flask import Flask, render_template_string
import time
import psutil

from detector import state
import detector.state as state
from detector.state import banned_ips, ip_request_counter

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>HNG Anomaly Dashboard</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body { font-family: Arial; background: #0f172a; color: white; margin: 30px; }
        .card { background: #1e293b; padding: 15px; margin: 10px; border-radius: 10px; }
        .danger { color: #ff4d4d; }
    </style>
</head>
<body>
    <h1>🚨 HNG Anomaly Detection Dashboard</h1>

    <div class="card">
        <h3>System Stats</h3>
        <p>CPU: {{cpu}}%</p>
        <p>Memory: {{mem}}%</p>
        <p>Uptime: {{uptime}} seconds</p>
    </div>

    <div class="card">
        <h3>Baseline</h3>
        <p>Mean: {{mean}}</p>
        <p>Std Dev: {{std}}</p>
    </div>

    <div class="card">
        <h3>Banned IPs</h3>
        {% for ip, meta in banned.items() %}
            <p class="danger">{{ip}} | {{meta['condition']}} | {{meta['duration']}}</p>
        {% endfor %}
    </div>

    <div class="card">
        <h3>Top IPs</h3>
        {% for ip, count in top_ips %}
            <p>{{ip}} : {{count}}</p>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route("/")
def dashboard():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    uptime = int(time.time() - state.start_time)

    top_ips = sorted(ip_request_counter.items(), key=lambda x: x[1], reverse=True)[:10]

    return render_template_string(
        HTML,
        cpu=cpu,
        mem=mem,
        uptime=uptime,
        mean=round(state.baseline_mean, 2),
        std=round(state.baseline_stddev, 2),
        banned=banned_ips,
        top_ips=top_ips
    )

def start_dashboard():
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
