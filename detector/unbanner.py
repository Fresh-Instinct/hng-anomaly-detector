#!/usr/bin/env python3
import time
import threading
from typing import List
from blocker import IPBlocker
from notifier import SlackNotifier

class Unbanner:
    def __init__(self, blocker: IPBlocker, notifier: SlackNotifier, 
                 unban_schedule: List[int]):
        self.blocker = blocker
        self.notifier = notifier
        self.unban_schedule = unban_schedule  # 👈 [600,1800,7200,86400]
        self.running = True
    
    def schedule_unbans(self):
        """Background thread - runs every 60s"""
        print("⏰ Auto-unbanner started")
        
        while self.running:
            for ip in list(self.blocker.banned_ips):
                self.check_unban_schedule(ip)
            time.sleep(60)  # Check every minute
    
    def check_unban_schedule(self, ip: str):
        """Check exact unban times: 10m, 30m, 2h, 24h"""
        if ip not in self.blocker.ban_timestamps:
            return
        
        ban_times = self.blocker.ban_timestamps[ip]
        now = time.time()
        
        # Check each scheduled unban
        for i, ban_time in enumerate(ban_times):
            duration = now - ban_time
            
            if i < len(self.unban_schedule) and duration > self.unban_schedule[i]:
                # EXECUTE UNBAN
                if self.blocker.unban_ip(ip):
                    duration_str = ["10min", "30min", "2hr", "24hr (perm)"][i]
                    self.notifier.send_alert(
                        f"✅ IP UNBANNED: {ip}",
                        f"Duration: {duration_str}\n"
                        f"Age: {duration/60:.0f}min",
                        "#00FF00"
                    )
                return  # One unban per check
    
    def stop(self):
        self.running = False
