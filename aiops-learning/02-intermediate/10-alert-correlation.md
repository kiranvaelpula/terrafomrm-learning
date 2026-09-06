# Alert Correlation

## Learning Objectives
- Understand alert correlation techniques
- Reduce alert noise and fatigue
- Group related alerts into incidents
- Implement intelligent alerting

---

## 📖 Understanding Alert Correlation (Intuition First)

Before the algorithms, let's understand why alert correlation might be the single most impactful AIOps capability for a tired operations team.

Imagine a car where every warning was wired to its own siren, and they all blared at maximum volume the moment anything went slightly off. Low washer fluid? SIREN. Tire pressure 1 PSI low? SIREN. Within a week you'd rip the whole system out — not because the warnings are wrong, but because you can't tell the *important* one from the trivial ones. That's exactly the state of modern monitoring: tens of thousands of alerts a day, 95% of them noise, drowning the handful that actually matter. This is **alert fatigue**, and it's dangerous — teams start ignoring alerts entirely, and the real outage slips through.

The core insight of alert correlation is that **one problem produces many alerts**. A single database slowdown doesn't cause one alert; it causes the database to alert, then the payment service (which depends on it) to alert, then the API gateway, then the frontend. Five, ten, fifty alerts — but *one incident*. Correlation is the art of recognizing that these alerts belong together and collapsing them into a single, understandable incident. Instead of "50 things are broken," the on-call engineer sees "1 incident: database overload, cascading to 5 services."

There are a few complementary ways to decide which alerts "belong together," and the intuition for each is natural. **Time-based correlation** says alerts firing within seconds of each other are probably related — a burst of alarms at 10:00:00 is likely one event, not fifty coincidences. **Topology-based correlation** is smarter: it uses the *service dependency graph* to understand that if the database is failing, alerts from everything downstream of it are expected symptoms, not separate problems. Combine them and you can even point at the likely **root cause** — the most upstream service in the affected chain.

The payoff is enormous and directly measurable. Reducing 10,000 alerts to 50 meaningful incidents isn't just tidier — it restores the team's ability to *trust* their alerts again. When every alert that reaches a human is real and pre-grouped with its context, response gets faster, engineers stop burning out, and the true signal never drowns in the noise. That's why correlation is often the first "wow" moment teams experience when adopting AIOps.

---

## The Alert Fatigue Problem

Modern systems generate thousands of alerts:
```
Daily Alert Volume:
- Before AIOps: 10,000+ alerts/day
- Meaningful alerts: ~50
- False positives: 95%+
- Time spent investigating: 8 hours/day
```

**Problem**: Operations teams can't keep up!

**Solution**: Alert correlation using AI

---

## Alert Correlation Techniques

### 1. Time-Based Correlation

Group alerts occurring in the same time window:

```python
from datetime import datetime, timedelta
import pandas as pd

class TimeBasedCorrelator:
    """Correlate alerts by time proximity"""
    
    def __init__(self, time_window=60):
        self.time_window = time_window  # seconds
    
    def correlate_alerts(self, alerts):
        """Group alerts by time"""
        
        df = pd.DataFrame(alerts)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        correlated_groups = []
        current_group = []
        
        for _, alert in df.iterrows():
            if not current_group:
                current_group.append(alert)
            else:
                time_diff = (alert['timestamp'] - current_group[-1]['timestamp']).total_seconds()
                
                if time_diff <= self.time_window:
                    current_group.append(alert)
                else:
                    correlated_groups.append(current_group)
                    current_group = [alert]
        
        if current_group:
            correlated_groups.append(current_group)
        
        return correlated_groups

# Usage
correlator = TimeBasedCorrelator(time_window=60)

alerts = [
    {'id': 1, 'timestamp': '2024-01-15T10:00:00', 'message': 'CPU high'},
    {'id': 2, 'timestamp': '2024-01-15T10:00:30', 'message': 'Memory high'},
    {'id': 3, 'timestamp': '2024-01-15T10:00:45', 'message': 'Disk I/O high'},
    {'id': 4, 'timestamp': '2024-01-15T10:05:00', 'message': 'Network latency'}
]

groups = correlator.correlate_alerts(alerts)
print(f"Grouped {len(alerts)} alerts into {len(groups)} incidents")
```

### 2. Topology-Based Correlation

Group alerts based on service dependencies:

```python
import networkx as nx

class TopologyCorrelator:
    """Correlate alerts using service topology"""
    
    def __init__(self):
        self.topology = nx.DiGraph()
        self.build_topology()
    
    def build_topology(self):
        """Build service dependency graph"""
        
        # Define service dependencies
        dependencies = [
            ('frontend', 'api-gateway'),
            ('api-gateway', 'auth-service'),
            ('api-gateway', 'payment-service'),
            ('payment-service', 'database'),
            ('payment-service', 'cache')
        ]
        
        self.topology.add_edges_from(dependencies)
    
    def find_root_cause_service(self, alerts):
        """Identify likely root cause based on topology"""
        
        affected_services = [alert['service'] for alert in alerts]
        
        # Find common upstream dependencies
        if len(affected_services) > 1:
            # Get upstream services for each affected service
            upstream_sets = []
            for service in affected_services:
                upstream = set(nx.ancestors(self.topology, service))
                upstream.add(service)
                upstream_sets.append(upstream)
            
            # Find common upstream services
            common_upstream = set.intersection(*upstream_sets)
            
            if common_upstream:
                # The most upstream service is likely the root cause
                root_cause = max(common_upstream, 
                               key=lambda s: len(nx.ancestors(self.topology, s)))
                return root_cause
        
        return affected_services[0] if affected_services else None
    
    def correlate_by_impact(self, alerts):
        """Group alerts by impact radius"""
        
        incidents = []
        
        for alert in alerts:
            service = alert['service']
            
            # Find downstream services (blast radius)
            downstream = list(nx.descendants(self.topology, service))
            
            # Check if other alerts are in blast radius
            related_alerts = [alert]
            for other_alert in alerts:
                if other_alert != alert and other_alert['service'] in downstream:
                    related_alerts.append(other_alert)
            
            if len(related_alerts) > 1:
                incidents.append({
                    'root_cause': service,
                    'affected_services': [a['service'] for a in related_alerts],
                    'alerts': related_alerts,
                    'blast_radius': len(downstream)
                })
        
        # Deduplicate incidents
        unique_incidents = self.deduplicate_incidents(incidents)
        
        return unique_incidents
    
    def deduplicate_incidents(self, incidents):
        """Remove duplicate incident groupings"""
        
        seen_alert_sets = set()
        unique = []
        
        for incident in incidents:
            alert_ids = tuple(sorted(a['id'] for a in incident['alerts']))
            
            if alert_ids not in seen_alert_sets:
                seen_alert_sets.add(alert_ids)
                unique.append(incident)
        
        return unique

# Usage
topo_correlator = TopologyCorrelator()

alerts = [
    {'id': 1, 'service': 'database', 'message': 'High latency'},
    {'id': 2, 'service': 'payment-service', 'message': 'Timeout errors'},
    {'id': 3, 'service': 'api-gateway', 'message': 'Increased errors'}
]

root_cause = topo_correlator.find_root_cause_service(alerts)
print(f"Likely root cause: {root_cause}")

incidents = topo_correlator.correlate_by_impact(alerts)
print(f"Correlated into {len(incidents)} incidents")
```

---

## 🎯 Interview Quick Points

- **Alert fatigue** is the core problem: thousands of alerts/day, ~95% noise, causing teams to ignore alerts
- The key insight: **one problem produces many alerts** across dependent services
- Correlation collapses many related alerts into a single, understandable **incident**
- **Time-based correlation**: alerts firing within a short window are likely the same event
- **Topology-based correlation**: uses the service **dependency graph** to know downstream alerts are symptoms
- Topology correlation can identify the likely **root cause** — the most upstream affected service
- **Blast radius** = the set of downstream services impacted by a failing service
- **Deduplication** prevents the same alert group from creating multiple incidents
- Typical impact: 10,000 alerts → ~50 meaningful incidents (huge noise reduction)
- The real payoff is **restored trust** — every alert reaching a human is real and pre-contextualized
- Correlation is often the first big "wow" win when adopting AIOps
- Best results combine time + topology (and often severity/type) rather than any single signal

