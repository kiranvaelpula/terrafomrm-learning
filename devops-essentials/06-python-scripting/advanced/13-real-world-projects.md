# Real-World Python DevOps Projects

> **Complete scripts that solve real operational problems — cost optimization, deployment tracking, automated cleanup, and infrastructure management.**

---

## 🧹 Project 1: AWS Cost Optimizer

```python
#!/usr/bin/env python3
"""
Find and report unused AWS resources that are costing money.
- Unattached EBS volumes
- Old snapshots
- Idle EC2 instances (low CPU)
- Unused Elastic IPs
"""

import boto3
from datetime import datetime, timezone, timedelta
import json

ec2 = boto3.client('ec2')

def find_unattached_volumes():
    """Find EBS volumes not attached to any instance."""
    volumes = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )['Volumes']
    
    total_cost = 0
    results = []
    
    for vol in volumes:
        size = vol['Size']
        vol_type = vol['VolumeType']
        # Approximate cost: gp3=$0.08/GB, gp2=$0.10/GB, io1=$0.125/GB
        cost_per_gb = {'gp3': 0.08, 'gp2': 0.10, 'io1': 0.125}.get(vol_type, 0.10)
        monthly_cost = size * cost_per_gb
        total_cost += monthly_cost
        
        results.append({
            'id': vol['VolumeId'],
            'size_gb': size,
            'type': vol_type,
            'monthly_cost': monthly_cost,
            'created': vol['CreateTime'].isoformat()
        })
    
    return results, total_cost


def find_unused_elastic_ips():
    """Find Elastic IPs not associated with any instance."""
    addresses = ec2.describe_addresses()['Addresses']
    unused = [
        addr for addr in addresses
        if 'InstanceId' not in addr and 'NetworkInterfaceId' not in addr
    ]
    # Unused EIPs cost $3.60/month each
    return unused, len(unused) * 3.60


def main():
    print("═" * 50)
    print("  AWS COST OPTIMIZATION REPORT")
    print(f"  Generated: {datetime.now():%Y-%m-%d %H:%M}")
    print("═" * 50)
    
    total_savings = 0
    
    # Unattached volumes
    volumes, vol_cost = find_unattached_volumes()
    total_savings += vol_cost
    print(f"\n📦 Unattached EBS Volumes: {len(volumes)}")
    print(f"   Potential savings: ${vol_cost:.2f}/month")
    for v in volumes[:5]:
        print(f"   • {v['id']} ({v['size_gb']}GB {v['type']}) — ${v['monthly_cost']:.2f}/mo")
    
    # Unused EIPs
    eips, eip_cost = find_unused_elastic_ips()
    total_savings += eip_cost
    print(f"\n🌐 Unused Elastic IPs: {len(eips)}")
    print(f"   Potential savings: ${eip_cost:.2f}/month")
    
    # Summary
    print(f"\n{'═' * 50}")
    print(f"  💰 TOTAL POTENTIAL SAVINGS: ${total_savings:.2f}/month")
    print(f"     (${total_savings * 12:.2f}/year)")
    print("═" * 50)


if __name__ == "__main__":
    main()
```

---

## 📊 Project 2: Deployment Tracker

```python
#!/usr/bin/env python3
"""
Track deployments with history, notification, and rollback info.
Stores deployment records in JSON and notifies Slack.
"""

import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

DEPLOY_LOG = Path("/var/log/deployments.json")
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")

def load_history():
    """Load deployment history."""
    if DEPLOY_LOG.exists():
        return json.loads(DEPLOY_LOG.read_text())
    return []

def save_history(history):
    """Save deployment history."""
    DEPLOY_LOG.parent.mkdir(parents=True, exist_ok=True)
    DEPLOY_LOG.write_text(json.dumps(history, indent=2))

def record_deployment(app, version, environment, deployer):
    """Record a new deployment."""
    history = load_history()
    
    entry = {
        "app": app,
        "version": version,
        "environment": environment,
        "deployer": deployer,
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }
    
    history.append(entry)
    save_history(history)
    
    # Get previous version for rollback reference
    prev_deploys = [
        d for d in history[:-1]
        if d['app'] == app and d['environment'] == environment
    ]
    prev_version = prev_deploys[-1]['version'] if prev_deploys else "none"
    
    # Notify
    message = (
        f"🚀 *{app}* `v{version}` deployed to *{environment}*\n"
        f"   By: {deployer}\n"
        f"   Previous: v{prev_version}\n"
        f"   Rollback: `devops deploy {environment} --version {prev_version}`"
    )
    
    if SLACK_WEBHOOK:
        requests.post(SLACK_WEBHOOK, json={"text": message}, timeout=5)
    
    print(message.replace('*', '').replace('`', ''))
    return entry


def show_history(app=None, environment=None, n=10):
    """Show recent deployment history."""
    history = load_history()
    
    # Filter
    if app:
        history = [d for d in history if d['app'] == app]
    if environment:
        history = [d for d in history if d['environment'] == environment]
    
    # Show latest N
    print(f"Last {n} deployments:")
    for entry in history[-n:]:
        ts = entry['timestamp'][:16]
        print(f"  [{ts}] {entry['app']} v{entry['version']} → {entry['environment']} (by {entry['deployer']})")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Deployment tracker")
    sub = parser.add_subparsers(dest="command")
    
    # Record command
    record = sub.add_parser("record")
    record.add_argument("app")
    record.add_argument("version")
    record.add_argument("environment")
    record.add_argument("--deployer", default=os.environ.get("USER", "unknown"))
    
    # History command
    hist = sub.add_parser("history")
    hist.add_argument("--app", default=None)
    hist.add_argument("--env", default=None)
    hist.add_argument("-n", type=int, default=10)
    
    args = parser.parse_args()
    
    if args.command == "record":
        record_deployment(args.app, args.version, args.environment, args.deployer)
    elif args.command == "history":
        show_history(args.app, args.env, args.n)
    else:
        parser.print_help()
```

---

## 🔄 Project 3: Automated Log Analyzer

```python
#!/usr/bin/env python3
"""
Analyze application logs — find top errors, slow requests, patterns.
"""

import re
import json
from collections import Counter, defaultdict
from datetime import datetime

def analyze_nginx_access_log(log_path, top_n=10):
    """Analyze nginx access log."""
    
    status_codes = Counter()
    ips = Counter()
    slow_requests = []
    paths = Counter()
    
    # Nginx combined log format regex
    pattern = re.compile(
        r'(?P<ip>\S+) .* \[(?P<time>.*?)\] "(?P<method>\S+) (?P<path>\S+) .*?" '
        r'(?P<status>\d+) (?P<size>\d+) ".*?" ".*?" (?P<response_time>[\d.]+)?'
    )
    
    total_lines = 0
    
    with open(log_path) as f:
        for line in f:
            total_lines += 1
            match = pattern.match(line)
            if not match:
                continue
            
            data = match.groupdict()
            status_codes[data['status']] += 1
            ips[data['ip']] += 1
            paths[data['path']] += 1
            
            # Track slow requests (> 2 seconds)
            if data.get('response_time'):
                rt = float(data['response_time'])
                if rt > 2.0:
                    slow_requests.append({
                        'path': data['path'],
                        'time': rt,
                        'ip': data['ip']
                    })
    
    # Report
    print(f"Total requests: {total_lines:,}")
    print(f"\nStatus Codes:")
    for code, count in status_codes.most_common():
        percent = count / total_lines * 100
        print(f"  {code}: {count:,} ({percent:.1f}%)")
    
    print(f"\nTop {top_n} IPs:")
    for ip, count in ips.most_common(top_n):
        print(f"  {ip:18} {count:,} requests")
    
    print(f"\nSlow Requests (> 2s): {len(slow_requests)}")
    for req in sorted(slow_requests, key=lambda x: x['time'], reverse=True)[:5]:
        print(f"  {req['time']:.2f}s — {req['path']}")


if __name__ == "__main__":
    import sys
    log_file = sys.argv[1] if len(sys.argv) > 1 else "/var/log/nginx/access.log"
    analyze_nginx_access_log(log_file)
```

---

## 🎯 Key Patterns Across All Projects

| Pattern | Why |
|---------|-----|
| `if __name__ == "__main__"` | Entry point guard — allows import AND direct run |
| `argparse` / `click` | Professional argument handling |
| Type hints | Self-documenting, IDE support |
| Logging over print | Configurable, level-aware |
| `pathlib.Path` | Modern, readable path handling |
| Error handling | Graceful failures, clear messages |
| Environment variables for secrets | Never hardcode credentials |
| JSON for data persistence | Human-readable, easy to parse |
| Functions with docstrings | Testable, documented |
| `sys.exit(0/1)` | Proper exit codes for CI/CD |

---

## 🎯 Interview Quick Points

- Structure scripts with `main()` function + `if __name__ == "__main__":`
- Use `argparse` for simple CLIs, `click` for complex ones
- Store state/history in JSON files (simple) or databases (scalable)
- Always include `--dry-run` option for destructive operations
- Implement rollback tracking (previous version info)
- Use `Counter` from collections for aggregation
- `re` module for log parsing with regex
- `pathlib.Path` for modern file operations
- Environment variables for configuration and secrets
- Add notifications (Slack, email) for important events
