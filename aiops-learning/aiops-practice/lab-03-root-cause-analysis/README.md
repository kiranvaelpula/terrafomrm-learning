# Lab 03: Root Cause Analysis with Causal Graphs

## Overview
Build an intelligent root cause analysis system using causal graphs to trace the origin of incidents across distributed systems.

**Duration:** 3-4 hours  
**Difficulty:** Advanced  
**Prerequisites:** Labs 01-02, Graph theory basics, Distributed systems knowledge

## Learning Objectives
- Model service dependencies as graphs
- Implement causal inference algorithms
- Trace incident propagation paths
- Calculate root cause probabilities
- Visualize dependency chains

## Lab Architecture

```
Metrics/Logs → Event Correlation → Causal Graph → RCA Engine → Root Cause Report
                        ↓              ↓              ↓
                   Time Series    Dependency      Bayesian
                   Analysis       Graph          Inference
```

## Setup

### 1. Install Dependencies

```bash
pip install networkx graphviz python-igraph \
    causalgraphicalmodels pgmpy \
    pandas numpy matplotlib seaborn
```

### 2. Sample System Topology

Create `data/system_topology.json`:

```json
{
  "services": [
    {"id": "frontend", "type": "web"},
    {"id": "api-gateway", "type": "api"},
    {"id": "auth-service", "type": "microservice"},
    {"id": "user-service", "type": "microservice"},
    {"id": "order-service", "type": "microservice"},
    {"id": "payment-service", "type": "microservice"},
    {"id": "database", "type": "database"},
    {"id": "cache", "type": "cache"},
    {"id": "message-queue", "type": "queue"}
  ],
  "dependencies": [
    {"from": "frontend", "to": "api-gateway"},
    {"from": "api-gateway", "to": "auth-service"},
    {"from": "api-gateway", "to": "user-service"},
    {"from": "api-gateway", "to": "order-service"},
    {"from": "order-service", "to": "payment-service"},
    {"from": "auth-service", "to": "database"},
    {"from": "user-service", "to": "database"},
    {"from": "user-service", "to": "cache"},
    {"from": "order-service", "to": "database"},
    {"from": "payment-service", "to": "database"},
    {"from": "order-service", "to": "message-queue"}
  ]
}
```

## Implementation

### Step 1: Dependency Graph Builder

Create `src/dependency_graph.py`:

```python
import networkx as nx
import json
from typing import Dict, List, Set
import matplotlib.pyplot as plt

class DependencyGraph:
    def __init__(self, topology_file: str):
        self.G = nx.DiGraph()
        self.load_topology(topology_file)
        
    def load_topology(self, filepath: str):
        """Load system topology from JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Add nodes
        for service in data['services']:
            self.G.add_node(
                service['id'],
                type=service['type']
            )
        
        # Add edges
        for dep in data['dependencies']:
            self.G.add_edge(dep['from'], dep['to'])
        
        print(f"✅ Loaded {len(self.G.nodes)} services with {len(self.G.edges)} dependencies")
    
    def get_dependencies(self, service: str) -> Set[str]:
        """Get all services this service depends on"""
        return set(self.G.successors(service))
    
    def get_dependents(self, service: str) -> Set[str]:
        """Get all services that depend on this service"""
        return set(self.G.predecessors(service))
    
    def get_impact_radius(self, service: str) -> Set[str]:
        """Get all services potentially affected by this service failing"""
        affected = set()
        
        # BFS to find all reachable nodes
        queue = [service]
        visited = {service}
        
        while queue:
            current = queue.pop(0)
            dependents = self.get_dependents(current)
            
            for dep in dependents:
                if dep not in visited:
                    affected.add(dep)
                    visited.add(dep)
                    queue.append(dep)
        
        return affected
    
    def find_critical_services(self) -> List[tuple]:
        """Find services with highest impact"""
        criticality = []
        
        for node in self.G.nodes():
            impact = len(self.get_impact_radius(node))
            criticality.append((node, impact))
        
        return sorted(criticality, key=lambda x: x[1], reverse=True)
    
    def visualize(self, highlight_nodes: List[str] = None):
        """Visualize dependency graph"""
        pos = nx.spring_layout(self.G, k=2, iterations=50)
        
        # Draw nodes
        node_colors = []
        for node in self.G.nodes():
            if highlight_nodes and node in highlight_nodes:
                node_colors.append('red')
            else:
                node_colors.append('lightblue')
        
        nx.draw_networkx_nodes(self.G, pos, node_color=node_colors, 
                               node_size=1000, alpha=0.9)
        nx.draw_networkx_labels(self.G, pos, font_size=8)
        nx.draw_networkx_edges(self.G, pos, edge_color='gray', 
                               arrows=True, arrowsize=20)
        
        plt.title("Service Dependency Graph")
        plt.axis('off')
        plt.tight_layout()
        return plt

# Test
if __name__ == "__main__":
    graph = DependencyGraph('../data/system_topology.json')
    
    # Find critical services
    critical = graph.find_critical_services()
    print("\n🔴 Critical Services (by impact):")
    for service, impact in critical[:5]:
        print(f"   {service}: affects {impact} services")
    
    # Check impact of database failure
    affected = graph.get_impact_radius('database')
    print(f"\n💥 Database failure would affect: {affected}")
    
    # Visualize
    plt = graph.visualize(highlight_nodes=['database'])
    plt.savefig('../data/dependency_graph.png', dpi=150, bbox_inches='tight')
    print("\n✅ Graph visualization saved")
```

### Step 2: Event Correlation Engine

Create `src/event_correlator.py`:

```python
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np

class EventCorrelator:
    def __init__(self, time_window_seconds=300):
        self.time_window = timedelta(seconds=time_window_seconds)
        
    def load_events(self, filepath: str) -> pd.DataFrame:
        """Load events from CSV"""
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        return df
    
    def find_correlated_events(self, events: pd.DataFrame) -> List[Dict]:
        """Find temporally correlated events"""
        correlations = []
        
        for idx, event in events.iterrows():
            # Find events within time window
            time_mask = (events['timestamp'] >= event['timestamp']) & \
                       (events['timestamp'] <= event['timestamp'] + self.time_window)
            
            correlated = events[time_mask]
            
            if len(correlated) > 1:
                correlations.append({
                    'trigger_event': event.to_dict(),
                    'correlated_events': correlated.to_dict('records'),
                    'time_span': (correlated['timestamp'].max() - 
                                 correlated['timestamp'].min()).total_seconds(),
                    'services_affected': correlated['service'].unique().tolist()
                })
        
        return correlations
    
    def calculate_temporal_proximity(self, event1: Dict, event2: Dict) -> float:
        """Calculate how close two events are in time"""
        t1 = pd.to_datetime(event1['timestamp'])
        t2 = pd.to_datetime(event2['timestamp'])
        
        time_diff = abs((t2 - t1).total_seconds())
        
        # Exponential decay: closer events have higher score
        return np.exp(-time_diff / 60)  # Decay over 60 seconds
    
    def build_event_sequence(self, events: pd.DataFrame) -> List[Dict]:
        """Build chronological event sequence"""
        sequence = []
        
        for idx, event in events.iterrows():
            sequence.append({
                'order': idx,
                'timestamp': event['timestamp'],
                'service': event['service'],
                'event_type': event['event_type'],
                'severity': event['severity']
            })
        
        return sequence

# Sample events data
sample_events = """timestamp,service,event_type,severity,message
2024-01-15 10:25:00,database,high_latency,warning,Query execution time increased
2024-01-15 10:25:15,order-service,timeout,error,Database connection timeout
2024-01-15 10:25:30,payment-service,timeout,error,Database connection timeout
2024-01-15 10:25:45,api-gateway,high_error_rate,critical,Increased 500 errors
2024-01-15 10:26:00,frontend,degraded_performance,warning,Slow page loads
"""

if __name__ == "__main__":
    # Save sample data
    with open('../data/sample_events.csv', 'w') as f:
        f.write(sample_events)
    
    correlator = EventCorrelator(time_window_seconds=120)
    events = correlator.load_events('../data/sample_events.csv')
    
    print("📊 Loaded events:")
    print(events[['timestamp', 'service', 'event_type', 'severity']])
    
    # Find correlations
    correlations = correlator.find_correlated_events(events)
    print(f"\n🔗 Found {len(correlations)} correlation groups")
```

### Step 3: Root Cause Analysis Engine

Create `src/rca_engine.py`:

```python
from dependency_graph import DependencyGraph
from event_correlator import EventCorrelator
import pandas as pd
from typing import List, Dict
import numpy as np

class RCAEngine:
    def __init__(self, topology_file: str):
        self.dep_graph = DependencyGraph(topology_file)
        self.correlator = EventCorrelator()
        
    def analyze_incident(self, events_file: str) -> Dict:
        """Perform root cause analysis"""
        print("🔍 Starting Root Cause Analysis...\n")
        
        # Load and correlate events
        events = self.correlator.load_events(events_file)
        correlations = self.correlator.find_correlated_events(events)
        
        # Get first event (potential root cause)
        first_event = events.iloc[0]
        
        # Calculate scores for each service
        scores = self.calculate_rca_scores(events)
        
        # Find propagation path
        propagation = self.trace_propagation(first_event['service'], 
                                            events['service'].tolist())
        
        return {
            'root_cause_candidates': scores,
            'first_event': first_event.to_dict(),
            'propagation_path': propagation,
            'total_services_affected': len(events['service'].unique()),
            'event_timeline': events.to_dict('records')
        }
    
    def calculate_rca_scores(self, events: pd.DataFrame) -> List[Dict]:
        """Calculate root cause probability for each service"""
        scores = []
        
        for service in events['service'].unique():
            service_events = events[events['service'] == service]
            
            # Factors for RCA scoring
            time_factor = 1.0 / (service_events['timestamp'].min().timestamp() + 1)
            severity_factor = (service_events['severity'] == 'critical').sum()
            dependency_factor = len(self.dep_graph.get_impact_radius(service))
            event_count = len(service_events)
            
            # Combined score
            score = (time_factor * 100 + 
                    severity_factor * 10 + 
                    dependency_factor * 5 +
                    event_count * 2)
            
            scores.append({
                'service': service,
                'rca_score': score,
                'first_event_time': service_events['timestamp'].min(),
                'impact_radius': dependency_factor,
                'severity_events': int(severity_factor)
            })
        
        return sorted(scores, key=lambda x: x['rca_score'], reverse=True)
    
    def trace_propagation(self, root_service: str, 
                         affected_services: List[str]) -> List[str]:
        """Trace how failure propagated through system"""
        path = [root_service]
        visited = {root_service}
        queue = [root_service]
        
        while queue:
            current = queue.pop(0)
            dependents = self.dep_graph.get_dependents(current)
            
            for dependent in dependents:
                if dependent in affected_services and dependent not in visited:
                    path.append(dependent)
                    visited.add(dependent)
                    queue.append(dependent)
        
        return path
    
    def generate_report(self, analysis: Dict):
        """Generate RCA report"""
        print("="*70)
        print("📋 ROOT CAUSE ANALYSIS REPORT")
        print("="*70)
        
        print(f"\n🎯 Top Root Cause Candidates:")
        for i, candidate in enumerate(analysis['root_cause_candidates'][:3], 1):
            print(f"\n{i}. {candidate['service']}")
            print(f"   RCA Score: {candidate['rca_score']:.2f}")
            print(f"   First Event: {candidate['first_event_time']}")
            print(f"   Impact Radius: {candidate['impact_radius']} services")
            print(f"   Critical Events: {candidate['severity_events']}")
        
        print(f"\n🌊 Propagation Path:")
        path = analysis['propagation_path']
        print(f"   {' → '.join(path)}")
        
        print(f"\n📊 Impact Summary:")
        print(f"   Total Services Affected: {analysis['total_services_affected']}")
        print(f"   Total Events: {len(analysis['event_timeline'])}")
        
        first = analysis['first_event']
        print(f"\n⏰ Timeline:")
        print(f"   First Event: {first['timestamp']}")
        print(f"   Service: {first['service']}")
        print(f"   Type: {first['event_type']}")
        
        print(f"\n💡 Recommendation:")
        root = analysis['root_cause_candidates'][0]
        print(f"   Investigate {root['service']} first")
        print(f"   Check logs starting from {root['first_event_time']}")
        print(f"   Monitor dependent services: {', '.join(analysis['propagation_path'][1:4])}")
        
        print("\n" + "="*70)

# Run RCA
if __name__ == "__main__":
    engine = RCAEngine('../data/system_topology.json')
    
    # Analyze incident
    analysis = engine.analyze_incident('../data/sample_events.csv')
    
    # Generate report
    engine.generate_report(analysis)
    
    # Visualize impact
    affected = [e['service'] for e in analysis['event_timeline']]
    plt = engine.dep_graph.visualize(highlight_nodes=affected)
    plt.savefig('../data/rca_impact.png', dpi=150, bbox_inches='tight')
    print("\n✅ Impact visualization saved")
```

### Step 4: Bayesian Network for Probabilistic RCA

Create `src/bayesian_rca.py`:

```python
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import numpy as np

class BayesianRCA:
    def __init__(self):
        self.model = None
        self.inference = None
        
    def build_network(self, dependencies: List[tuple]):
        """Build Bayesian Network from dependencies"""
        self.model = BayesianNetwork(dependencies)
        
    def add_cpds(self, cpds: Dict):
        """Add Conditional Probability Distributions"""
        for node, cpd_data in cpds.items():
            cpd = TabularCPD(
                variable=node,
                variable_card=2,  # Binary: healthy(0) or failed(1)
                values=cpd_data['values'],
                evidence=cpd_data.get('evidence'),
                evidence_card=cpd_data.get('evidence_card')
            )
            self.model.add_cpds(cpd)
        
        # Validate model
        assert self.model.check_model()
        self.inference = VariableElimination(self.model)
    
    def infer_root_cause(self, observations: Dict) -> Dict:
        """Infer root cause given observations"""
        results = {}
        
        # Query each potential root cause
        for node in self.model.nodes():
            if node not in observations:
                # Calculate probability this is root cause
                prob = self.inference.query(
                    variables=[node],
                    evidence=observations
                )
                results[node] = prob.values[1]  # P(failed)
        
        return results

# Example usage
if __name__ == "__main__":
    rca = BayesianRCA()
    
    # Define network structure
    dependencies = [
        ('database', 'order-service'),
        ('database', 'payment-service'),
        ('order-service', 'api-gateway'),
        ('payment-service', 'api-gateway'),
        ('api-gateway', 'frontend')
    ]
    
    rca.build_network(dependencies)
    
    # Define CPDs (simplified example)
    cpds = {
        'database': {
            'values': [[0.95], [0.05]]  # P(healthy), P(failed)
        },
        'order-service': {
            'values': [
                [0.98, 0.30],  # P(healthy | db_healthy), P(healthy | db_failed)
                [0.02, 0.70]   # P(failed | db_healthy), P(failed | db_failed)
            ],
            'evidence': ['database'],
            'evidence_card': [2]
        }
        # ... add more CPDs
    }
    
    # rca.add_cpds(cpds)
    print("✅ Bayesian Network built (CPDs need to be completed)")
```

## Exercises

### Exercise 1: Enhanced Correlation
Implement advanced correlation:
- Cross-correlation with lag analysis
- Granger causality testing
- Mutual information scoring

### Exercise 2: ML-based RCA
Train a model to predict root causes:
```python
from sklearn.ensemble import RandomForestClassifier

# Features: timing, severity, dependencies
# Target: is_root_cause (boolean)
```

### Exercise 3: Real-time RCA
Build streaming RCA engine:
- Incremental graph updates
- Online learning
- Alert generation

## Validation

Run the complete RCA pipeline:

```bash
python src/dependency_graph.py
python src/event_correlator.py
python src/rca_engine.py
```

Expected output:
- Dependency graph visualization
- RCA scores for all services
- Propagation path trace
- Confidence scores

## Key Takeaways

✅ Dependency graphs model service relationships  
✅ Temporal correlation identifies event sequences  
✅ Graph traversal traces failure propagation  
✅ Bayesian inference calculates root cause probabilities  
✅ Automation reduces MTTR significantly

## Next Steps

- **Lab 04**: Predictive analytics with time series forecasting
- Integrate with incident management tools
- Add automated remediation triggers
- Build RCA knowledge base

## Resources

- [Causal Inference](https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/)
- [Bayesian Networks](https://pgmpy.org/)
- [NetworkX](https://networkx.org/)
