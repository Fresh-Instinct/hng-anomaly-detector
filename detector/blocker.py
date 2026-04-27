#!/usr/bin/env python3
import iptc
import time
from typing import List, Set

class IPBlocker:
    def __init__(self):
        self.banned_ips: Set[str] = set()
        self.ban_timestamps: dict[str, list[float]] = {}
    
    def ban_ip(self, ip: str) -> bool:
        """Add iptables DROP rule - PER-IP ANOMALY ONLY"""
        if ip in self.banned_ips:
            return False
        
        try:
            # Create DROP rule for INPUT chain
            table = iptc.Table(iptc.Table.FILTER)
            chain = iptc.Chain(table, "INPUT")
            
            rule = iptc.Rule()
            rule.src = ip  # Source IP match
            target = iptc.Target(rule, "DROP")
            rule.target = target
            
            chain.insert_rule(rule)  # Insert at top
            self.banned_ips.add(ip)
            self.ban_timestamps[ip] = [time.time()]  # Track ban time
            
            print(f"🚫 BLOCKED {ip} via iptables")
            return True
            
        except Exception as e:
            print(f"❌ iptables ban failed for {ip}: {e}")
            return False
    
    def unban_ip(self, ip: str) -> bool:
        """Remove iptables rule"""
        if ip not in self.banned_ips:
            return False
        
        try:
            table = iptc.Table(iptc.Table.FILTER)
            chain = iptc.Chain(table, "INPUT")
            
            # Remove first matching rule
            for i, rule in enumerate(chain.rules):
                if rule.src == ip and rule.target.name == "DROP":
                    chain.delete_rule(i)
                    break
            
            self.banned_ips.discard(ip)
            del self.ban_timestamps[ip]
            print(f"✅ UNBANNED {ip}")
            return True
            
        except Exception as e:
            print(f"❌ iptables unban failed for {ip}: {e}")
            return False
    
    def is_banned(self, ip: str) -> bool:
        return ip in self.banned_ips
    
    def get_banned_ips(self) -> List[str]:
        """For dashboard"""
        return sorted(list(self.banned_ips))
    
    def get_ban_age(self, ip: str) -> float:
        if ip in self.ban_timestamps:
            return time.time() - self.ban_timestamps[ip][0]
        return 0
