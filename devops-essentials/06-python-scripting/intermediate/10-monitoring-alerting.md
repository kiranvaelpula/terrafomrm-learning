# Monitoring and Alerting Scripts

> **Custom monitoring scripts check system health, application metrics, and send alerts when thresholds are breached.**

---

## 📖 Why Custom Monitoring?

Tools like Prometheus and Datadog are great, but sometimes you need:
- Quick custom checks specific to your app
- Lightweight monitoring without full stack
- Integration between systems
- Custom alerting logic

```bash
pip install psutil requests
```

---

## 📊 System Monitoring with psutil

```python
import psutil
import platform
from datetime import datetime

def get_system_info():
    """Collect comprehensive system metrics."""
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)     # 1 sec sample
    cpu_count = psutil.cpu_count()
    load_avg = psutil.getloadavg()                   # 1, 5, 15 min
    
    # Memory
    mem = psutil.virtual_memory()
    # mem.total, mem.available, mem.percent, mem.used
    
    # Disk
    disk = psutil.disk_usage('/')
    # disk.total, disk.used, disk.free, disk.percent
    
    # Network
    net = psutil.net_io_counters()
    # net.bytes_sent, net.bytes_recv
    
    # System info
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    return {
        "hostname": platform.node(),
        "cpu_percent": cpu_percent,
        "cpu_cores": cpu_count,
        "load_avg_1m": load_avg[0],
        "memory_percent": mem.percent,
        "memory_used_gb": mem.used / (1024**3),
        "memory_total_gb": mem.total / (1024**3),
        "disk_percent": disk.percent,
        "disk_free_gb": disk.free / (1024**3),
        "uptime_hours": uptime.total_seconds() / 3600,
        "net_sent_mb": net.bytes_sent / (1024**2),
        "net_recv_mb": net.bytes_recv / (1024**2),
    }

info = get_system_info()
for key, value in info.items():
    print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
```

---

## 🔔 Complete Monitoring + Alerting Script

```python
#!/usr/bin/env python3
"""
Server monitoring script with Slack alerts.
Run via cron: */5 * * * * /opt/scripts/monitor.py
"""

import psutil
import requests
import os
import sys
import subprocess
import logging
from datetime import datetime

# ── Configuration ──
THRESHOLDS = {
    "cpu": {"warn": 70, "crit": 90},
    "memory": {"warn": 80, "crit": 95},
    "disk": {"warn": 75, "crit": 90},
}

SERVICES = ["nginx", "docker", "postgresql"]
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK", "")
HOSTNAME = os.uname().nodename

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger()

# ── Check Functions ──
def check_cpu():
    """Check CPU usage."""
    usage = psutil.cpu_percent(interval=2)
    if usage > THRESHOLDS["cpu"]["crit"]:
        return "critical", f"CPU CRITICAL: {usage}%"
    elif usage > THRESHOLDS["cpu"]["warn"]:
        return "warning", f"CPU WARNING: {usage}%"
    return "ok", f"CPU: {usage}%"

def check_memory():
    """Check memory usage."""
    mem = psutil.virtual_memory()
    if mem.percent > THRESHOLDS["memory"]["crit"]:
        return "critical", f"Memory CRITICAL: {mem.percent}%"
    elif mem.percent > THRESHOLDS["memory"]["warn"]:
        return "warning", f"Memory WARNING: {mem.percent}%"
    return "ok", f"Memory: {mem.percent}%"

def check_disk():
    """Check disk usage for all mounted partitions."""
    alerts = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            if usage.percent > THRESHOLDS["disk"]["crit"]:
                alerts.append(("critical", f"Disk CRITICAL: {partition.mountpoint} at {usage.percent}%"))
            elif usage.percent > THRESHOLDS["disk"]["warn"]:
                alerts.append(("warning", f"Disk WARNING: {partition.mountpoint} at {usage.percent}%"))
        except PermissionError:
            continue
    return alerts

def check_services():
    """Check if required services are running."""
    alerts = []
    for service in SERVICES:
        result = subprocess.run(
            ["systemctl", "is-active", service],
            capture_output=True, text=True
        )
        if result.stdout.strip() != "active":
            alerts.append(("critical", f"Service DOWN: {service}"))
    return alerts

# ── Alert Function ──
def send_alert(level, message):
    """Send alert to Slack."""
    if not SLACK_WEBHOOK:
        logger.warning("SLACK_WEBHOOK not set, alert not sent")
        return
    
    color = {"critical": "danger", "warning": "warning"}.get(level, "good")
    emoji = {"critical": "🔴", "warning": "🟡"}.get(level, "🟢")
    
    payload = {
        "attachments": [{
            "color": color,
            "title": f"{emoji} Alert: {HOSTNAME}",
            "text": message,
            "footer": f"Monitor | {datetime.now():%Y-%m-%d %H:%M:%S}"
        }]
    }
    
    try:
        requests.post(SLACK_WEBHOOK, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")


# ── Main ──
def main():
    logger.info(f"Running health check on {HOSTNAME}")
    
    all_alerts = []
    
    # Run checks
    level, msg = check_cpu()
    if level != "ok":
        all_alerts.append((level, msg))
    
    level, msg = check_memory()
    if level != "ok":
        all_alerts.append((level, msg))
    
    all_alerts.extend(check_disk())
    all_alerts.extend(check_services())
    
    # Report
    if all_alerts:
        # Determine highest severity
        has_critical = any(level == "critical" for level, _ in all_alerts)
        overall_level = "critical" if has_critical else "warning"
        
        message = "\n".join(f"• {msg}" for _, msg in all_alerts)
        logger.warning(f"Alerts detected:\n{message}")
        send_alert(overall_level, message)
        sys.exit(1)
    else:
        logger.info("All checks passed ✓")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## 📊 Process Monitoring

```python
def find_top_processes(n=5):
    """Find top N processes by CPU and memory."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            if info['cpu_percent'] is not None:
                processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Top by CPU
    print("Top by CPU:")
    for p in sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:n]:
        print(f"  {p['name']:20} PID:{p['pid']:6} CPU:{p['cpu_percent']:.1f}%")
    
    # Top by Memory
    print("Top by Memory:")
    for p in sorted(processes, key=lambda x: x['memory_percent'] or 0, reverse=True)[:n]:
        print(f"  {p['name']:20} PID:{p['pid']:6} MEM:{p['memory_percent']:.1f}%")
```

---

## 🎯 Interview Quick Points

- `psutil` provides cross-platform system monitoring
- `psutil.cpu_percent(interval=1)` — interval needed for accurate reading
- `psutil.virtual_memory()` → `.percent`, `.used`, `.total`, `.available`
- `psutil.disk_usage('/')` → `.percent`, `.free`, `.total`
- `psutil.process_iter(['name', 'cpu_percent'])` for process list
- Combine with Slack webhooks for alerting
- Use thresholds (warn/critical) to avoid alert fatigue
- Run via cron for scheduled monitoring
- `systemctl is-active` checks service status
- Log all checks for historical analysis
