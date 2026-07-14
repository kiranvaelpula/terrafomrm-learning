# Graph Analytics for Topology

## Learning Objectives
- Model IT infrastructure as graphs
- Analyze service dependencies
- Detect failure propagation
- Identify critical components

---

## Why Graph Analytics?

Modern IT systems are interconnected networks:
- Services depend on other services
- Failures propagate through dependencies
- Understanding topology is key to RCA

**Graph analytics helps:**
- Visualize dependencies
- Find blast radius of failures
- Identify single points of failure
- Optimize architecture

---

## Building Service Dependency Graph

```python
import networkx as nx
import matplotlib.pyplot as plt

class ServiceTopologyGraph:
    """Model service topology as a graph"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def add_service(self, service_name, metadata=None):
        """Add service node"""
        self.graph.add_node(service_name, **(metadata or {}))
    
    def add_dependency(self, service, depends_on, metadata=None):
        """Add dependency edge"""
        self.graph.add_edge(service, depends_on, **(metadata or {}))
    
    def build_from_config(self, services_config):
        """Build graph from configuration"""
        
        for service in services_config:
            self.add_service(
                service['name'],
                metadata={
                    'type': service.get('type', 'service'),
                    'criticality': service.get('criticality', 'medium')
                }
            )
            
            for dep in service.get('dependencies', []):
                self.add_dependency(service['name'], dep)
        
        return self.graph
    
    def get_dependencies(self, service):
        """Get direct dependencies of a service"""
        return list(self.graph.successors(service))
    
    def get_dependents(self, service):
        """Get services that depend on this service"""
        return list(self.graph.predecessors(service))
    
    def get_all_downstream(self, service):
        """Get all services downstream (blast radius)"""
        return list(nx.descendants(self.graph, service))
    
    def get_all_upstream(self, service):
        """Get all services upstream"""
        return list(nx.ancestors(self.graph, service))
    
    def visualize(self, highlight_service=None):
        """Visualize the graph"""
        
        pos = nx.spring_layout(self.graph)
        
        # Color nodes
        node_colors = []
        for node in self.graph.nodes():
            if node == highlight_service:
                node_colors.append('red')
            elif highlight_service and node in self.get_all_downstream(highlight_service):
                node_colors.append('orange')
            else:
                node_colors.append('lightblue')
        
        plt.figure(figsize=(12, 8))
        nx.draw(self.graph, pos, 
                node_color=node_colors,
                with_labels=True,
                node_size=3000,
                font_size=10,
                arrows=True)
        
        plt.title("Service Dependency Graph")
        plt.show()

# Usage
topo = ServiceTopologyGraph()

# Define services
services = [
    {
        'name': 'frontend',
        'dependencies': ['api-gateway'],
        'criticality': 'high'
    },
    {
        'name': 'api-gateway',
        'dependencies': ['auth-service', 'payment-service'],
        'criticality': 'high'
    },
    {
        'name': 'auth-service',
        'dependencies': ['user-db'],
        'criticality': 'critical'
    },
    {
        'name': 'payment-service',
        'dependencies': ['payment-db', 'cache'],
        'criticality': 'critical'
    },
    {
        'name': 'user-db',
        'dependencies': [],
        'type': 'database'
    },
    {
        'name': 'payment-db',
        'dependencies': [],
        'type': 'database'
    },
    {
        'name': 'cache',
        'dependencies': [],
        'type': 'cache'
    }
]

topo.build_from_config(services)

# Analyze
print(f"Dependencies of api-gateway: {topo.get_dependencies('api-gateway')}")
print(f"Services depending on user-db: {topo.get_dependents('user-db')}")
print(f"Blast radius of payment-db failure: {topo.get_all_upstream('payment-db')}")
```

---

## Failure Impact Analysis

```python
class FailureImpactAnalyzer:
    """Analyze impact of service failures"""
    
    def __init__(self, topology_graph):
        self.graph = topology_graph.graph
    
    def calculate_blast_radius(self, failed_service):
        """Calculate impact of service failure"""
        
        # Get all affected services
        affected = set(nx.ancestors(self.graph, failed_service))
        affected.add(failed_service)
        
        # Calculate impact metrics
        total_services = len(self.graph.nodes())
        affected_count = len(affected)
        impact_percentage = (affected_count / total_services) * 100
        
        # Identify critical affected services
        critical_affected = [
            service for service in affected
            if self.graph.nodes[service].get('criticality') == 'critical'
        ]
        
        return {
            'failed_service': failed_service,
            'affected_services': list(affected),
            'affected_count': affected_count,
            'impact_percentage': impact_percentage,
            'critical_affected': critical_affected
        }
    
    def find_single_points_of_failure(self):
        """Identify services whose failure affects many others"""
        
        spofs = []
        
        for node in self.graph.nodes():
            impact = self.calculate_blast_radius(node)
            
            if impact['impact_percentage'] > 50:  # Affects >50% of services
                spofs.append({
                    'service': node,
                    'impact': impact
                })
        
        # Sort by impact
        spofs.sort(key=lambda x: x['impact']['impact_percentage'], reverse=True)
        
        return spofs
    
    def simulate_cascade_failure(self, initial_failure):
        """Simulate how failures cascade through system"""
        
        failed = {initial_failure}
        cascade_steps = [{'step': 0, 'failed': [initial_failure]}]
        
        step = 1
        while True:
            newly_failed = set()
            
            # Check each service
            for service in self.graph.nodes():
                if service in failed:
                    continue
                
                # Get dependencies
                deps = list(self.graph.successors(service))
                
                # If all critical dependencies are down, service fails
                if deps and all(d in failed for d in deps):
                    newly_failed.add(service)
            
            if not newly_failed:
                break
            
            failed.update(newly_failed)
            cascade_steps.append({
                'step': step,
                'failed': list(newly_failed)
            })
            
            step += 1
        
        return {
            'initial_failure': initial_failure,
            'total_failed': len(failed),
            'cascade_steps': cascade_steps
        }
    
    def recommend_redundancy(self):
        """Recommend where to add redundancy"""
        
        recommendations = []
        
        # Find bottleneck services
        spofs = self.find_single_points_of_failure()
        
        for spof in spofs:
            service = spof['service']
            
            # Check if service has redundancy
            if not self.has_redundancy(service):
                recommendations.append({
                    'service': service,
                    'reason': f"Single point of failure affecting {spof['impact']['impact_percentage']:.1f}% of system",
                    'recommendation': f"Add redundancy/failover for {service}"
                })
        
        return recommendations
    
    def has_redundancy(self, service):
        """Check if service has redundancy"""
        # Simplified check - in reality, query service mesh or config
        return False

# Usage
analyzer = FailureImpactAnalyzer(topo)

# Analyze impact of database failure
impact = analyzer.calculate_blast_radius('payment-db')
print(f"Impact of payment-db failure:")
print(f"  Affected services: {impact['affected_count']}")
print(f"  Impact: {impact['impact_percentage']:.1f}%")
print(f"  Affected: {impact['affected_services']}")

# Find SPOFs
spofs = analyzer.find_single_points_of_failure()
print(f"\nSingle points of failure: {len(spofs)}")
for spof in spofs:
    print(f"  {spof['service']}: {spof['impact']['impact_percentage']:.1f}% impact")

# Simulate cascade
cascade = analyzer.simulate_cascade_failure('user-db')
print(f"\nCascade failure from user-db:")
for step in cascade['cascade_steps']:
    print(f"  Step {step['step']}: {step['failed']}")
```

---

## Centrality Analysis

```python
class ServiceCentralityAnalyzer:
    """Analyze importance of services using centrality metrics"""
    
    def __init__(self, topology_graph):
        self.graph = topology_graph.graph
    
    def calculate_betweenness_centrality(self):
        """Services that are bridges between other services"""
        
        centrality = nx.betweenness_centrality(self.graph)
        
        # Sort by centrality
        sorted_services = sorted(
            centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {'service': service, 'centrality': score}
            for service, score in sorted_services
        ]
    
    def calculate_pagerank(self):
        """Services ranked by importance (like Google PageRank)"""
        
        pagerank = nx.pagerank(self.graph)
        
        sorted_services = sorted(
            pagerank.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {'service': service, 'rank': score}
            for service, score in sorted_services
        ]
    
    def find_critical_paths(self, source, target):
        """Find all paths between two services"""
        
        try:
            paths = list(nx.all_simple_paths(self.graph, source, target))
            
            # Identify services on all paths (critical)
            all_paths_services = set(paths[0]) if paths else set()
            for path in paths[1:]:
                all_paths_services &= set(path)
            
            return {
                'paths': paths,
                'critical_services': list(all_paths_services)
            }
        except nx.NetworkXNoPath:
            return {'paths': [], 'critical_services': []}
    
    def identify_service_tiers(self):
        """Identify service layers/tiers"""
        
        # Topological sort to get layers
        try:
            layers = list(nx.topological_generations(self.graph))
            
            tiers = {}
            for tier_num, tier_services in enumerate(layers):
                tiers[f'tier_{tier_num}'] = list(tier_services)
            
            return tiers
        except nx.NetworkXError:
            return {'error': 'Graph has cycles'}

# Usage
centrality = ServiceCentralityAnalyzer(topo)

# Betweenness centrality
betweenness = centrality.calculate_betweenness_centrality()
print("Most critical services (betweenness):")
for item in betweenness[:3]:
    print(f"  {item['service']}: {item['centrality']:.3f}")

# PageRank
pagerank = centrality.calculate_pagerank()
print("\nMost important services (PageRank):")
for item in pagerank[:3]:
    print(f"  {item['service']}: {item['rank']:.3f}")

# Service tiers
tiers = centrality.identify_service_tiers()
print("\nService tiers:")
for tier, services in tiers.items():
    print(f"  {tier}: {services}")
```

---

## Real-Time Topology Discovery

```python
import requests
from kubernetes import client, config

class TopologyDiscovery:
    """Discover service topology automatically"""
    
    def discover_from_kubernetes(self):
        """Discover services from Kubernetes"""
        
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
        services = v1.list_service_for_all_namespaces()
        
        topology = ServiceTopologyGraph()
        
        for svc in services.items:
            service_name = f"{svc.metadata.namespace}/{svc.metadata.name}"
            topology.add_service(service_name, metadata={
                'namespace': svc.metadata.namespace,
                'type': svc.spec.type
            })
        
        return topology
    
    def discover_from_service_mesh(self):
        """Discover from service mesh (Istio/Linkerd)"""
        
        # Query service mesh API
        # This is a simplified example
        
        topology = ServiceTopologyGraph()
        
        # Get service graph from mesh
        mesh_data = self.query_service_mesh()
        
        for edge in mesh_data['edges']:
            topology.add_dependency(
                edge['source'],
                edge['target'],
                metadata={'traffic_rate': edge.get('requests_per_second')}
            )
        
        return topology
    
    def discover_from_apm(self):
        """Discover from APM traces"""
        
        # Analyze traces to build dependency graph
        traces = self.get_traces_sample()
        
        topology = ServiceTopologyGraph()
        
        for trace in traces:
            for i in range(len(trace['spans']) - 1):
                source = trace['spans'][i]['service']
                target = trace['spans'][i+1]['service']
                
                if not topology.graph.has_edge(source, target):
                    topology.add_dependency(source, target)
        
        return topology
    
    def query_service_mesh(self):
        """Query service mesh for topology"""
        # Placeholder
        return {'edges': []}
    
    def get_traces_sample(self):
        """Get sample traces from APM"""
        # Placeholder
        return []

# Usage
discovery = TopologyDiscovery()
topology = discovery.discover_from_kubernetes()
```

---

## Graph-Based Root Cause Analysis

```python
class GraphBasedRCA:
    """Root cause analysis using graph traversal"""
    
    def __init__(self, topology):
        self.topology = topology
    
    def find_root_cause(self, failed_services, alerts):
        """Find root cause by analyzing graph and alerts"""
        
        # Build failure subgraph
        failure_graph = self.build_failure_subgraph(failed_services)
        
        # Find common upstream dependencies
        common_upstream = self.find_common_dependencies(failed_services)
        
        # Score each candidate
        candidates = []
        for service in common_upstream:
            score = self.calculate_root_cause_score(
                service,
                failed_services,
                alerts
            )
            candidates.append({'service': service, 'score': score})
        
        # Sort by score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return candidates[0] if candidates else None
    
    def build_failure_subgraph(self, failed_services):
        """Build subgraph of failed services"""
        
        nodes = set(failed_services)
        for service in failed_services:
            nodes.update(self.topology.get_all_upstream(service))
            nodes.update(self.topology.get_all_downstream(service))
        
        return self.topology.graph.subgraph(nodes)
    
    def find_common_dependencies(self, failed_services):
        """Find services that are upstream of all failures"""
        
        if not failed_services:
            return set()
        
        common = set(self.topology.get_all_upstream(failed_services[0]))
        
        for service in failed_services[1:]:
            upstream = set(self.topology.get_all_upstream(service))
            common &= upstream
        
        return common
    
    def calculate_root_cause_score(self, candidate, failed_services, alerts):
        """Score likelihood of being root cause"""
        
        score = 0
        
        # Higher score if it affects all failed services
        affected = self.topology.get_all_upstream(candidate)
        affected_failed = sum(1 for s in failed_services if s in affected)
        score += (affected_failed / len(failed_services)) * 50
        
        # Higher score if it has alerts
        service_alerts = [a for a in alerts if a['service'] == candidate]
        score += len(service_alerts) * 10
        
        # Higher score if alerts are earlier
        if service_alerts:
            earliest_alert = min(a['timestamp'] for a in service_alerts)
            # Earlier alerts score higher
            score += 20
        
        return score

# Usage
rca = GraphBasedRCA(topo)

failed = ['frontend', 'api-gateway']
alerts = [
    {'service': 'user-db', 'timestamp': '10:00:00', 'message': 'High latency'},
    {'service': 'frontend', 'timestamp': '10:00:30', 'message': 'Errors'},
]

root_cause = rca.find_root_cause(failed, alerts)
print(f"Root cause: {root_cause['service']} (score: {root_cause['score']})")
```

---

## Summary

Graph analytics for AIOps enables:
- Service dependency visualization
- Failure impact analysis
- SPOF identification
- Graph-based RCA
- Automated topology discovery

**Key algorithms:**
- Graph traversal
- Centrality metrics
- Path finding
- Community detection

---

**Next**: [Reinforcement Learning →](16-rl-auto-remediation.md)
