# 🚀 HNG Anomaly Detector

## 🖥️ LIVE URLS
**Dashboard**: `http://YOUR_IP:8080` ← **SUBMIT THIS**

## ✅ TECHNICAL SPECS MET
- **Sliding Window**: `deque(maxlen=60)` per-IP + global
- **Baseline**: 30min rolling mean/stddev, recalc 60s
- **Detection**: Z-score>3.0 **OR** 5x multiplier (first to fire)
- **Logs**: JSON to `HNG-nginx-logs` volume (read-only)
- **Response**: `iptables DROP` + Slack + auto-unban `[10m,30m,2h,24h]`

## 🛠️ Deploy
```bash
curl -L https://github.com/YOUR_USERNAME/hng-anomaly-detector/raw/main/deploy.sh | bash
