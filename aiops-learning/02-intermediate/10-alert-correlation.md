# Alert Correlation

## Learning Objectives
- Understand alert correlation techniques
- Reduce alert noise and fatigue
- Group related alerts into incidents
- Implement intelligent alerting

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

