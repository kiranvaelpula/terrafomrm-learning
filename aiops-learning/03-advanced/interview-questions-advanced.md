# AIOps Interview Questions - Advanced Level

Advanced interview questions covering time series forecasting, NLP for IT ops, distributed systems, and production AIOps at scale.

---

## Time Series Forecasting

### Q1: How do you forecast capacity needs for a cloud infrastructure using time series analysis?

**Answer:**

**Approach:**

1. **Data Collection** - Historical metrics (CPU, memory, requests)
2. **Feature Engineering** - Time-based features, seasonality
3. **Model Selection** - ARIMA, Prophet, or LSTM
4. **Forecasting** - Predict 7-30 days ahead
5. **Alerting** - Trigger capacity planning when threshold reached

**Implementation:**
```python
from prophet import Prophet
import pandas as pd
import numpy as np

def forecast_capacity(historical_data, days_ahead=30):
    """Forecast infrastructure capacity needs"""
    
    # Prepare data for Prophet
    df = pd.DataFrame({
        'ds': historical_data['timestamp'],
        'y': historical_data['cpu_usage']
    })
    
    # Add regressors for special events
    df['is_holiday'] = historical_data['is_holiday']
    df['deployment_day'] = historical_data['deployment_day']
    
    # Initialize and configure Prophet
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=True,
        holidays=holidays_df,
        changepoint_prior_scale=0.05  # Flexibility in trend
    )
    
    # Add custom regressors
    model.add_regressor('is_holiday')
    model.add_regressor('deployment_day')
    
    # Fit model
    model.fit(df)
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=days_ahead)
    future['is_holiday'] = 0  # Set default values
    future['deployment_day'] = 0
    
    # Forecast
    forecast = model.predict(future)
    
    # Extract predictions
    predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    
    # Check if capacity will be exceeded
    capacity_threshold = 80  # 80% usage
    capacity_issues = predictions[predictions['yhat'] > capacity_threshold]
    
    if not capacity_issues.empty:
        first_issue_date = capacity_issues.iloc[0]['ds']
        alert(f"Capacity will exceed {capacity_threshold}% on {first_issue_date}")
        return {
            'forecast': predictions,
            'alert': True,
            'alert_date': first_issue_date,
            'recommended_action': 'Scale up infrastructure'
        }
    
    return {
        'forecast': predictions,
        'alert': False
    }

# Usage
historical_metrics = fetch_metrics(days=90)
capacity_forecast = forecast_capacity(historical_metrics, days_ahead=30)

if capacity_forecast['alert']:
    print(f"⚠️ Alert: {capacity_forecast['alert_date']}")
    print(f"Action: {capacity_forecast['recommended_action']}")
```

**Key Considerations:**
- Account for seasonality (daily, weekly, yearly)
- Include special events (holidays, product launches)
- Model uncertainty with confidence intervals
- Validate against historical data
- Update model regularly with new data

---

**Key Considerations:**
- Account for seasonality (daily, weekly, yearly)
- Include special events (holidays, product launches)
- Model uncertainty with confidence intervals
- Validate against historical data
- Update model regularly with new data

---

### Q2: Compare ARIMA, Prophet, and LSTM for AIOps time series forecasting.

**Answer:**

| Feature | ARIMA | Prophet | LSTM |
|---------|-------|---------|------|
| **Type** | Statistical | Statistical + ML | Deep Learning |
| **Training Time** | Fast | Fast | Slow |
| **Data Requirements** | Medium | Medium | Large |
| **Seasonality** | Manual | Automatic | Learns |
| **Missing Data** | Poor | Good | Medium |
| **Interpretability** | High | High | Low |
| **Trend Changes** | Poor | Good | Excellent |
| **Best For** | Stable patterns | Business metrics | Complex patterns |

**When to Use Each:**

**ARIMA**: 
```python
# Stable, stationary data with clear patterns
from statsmodels.tsa.arima.model import ARIMA

model = ARIMA(data, order=(1,1,1))
forecast = model.fit().forecast(steps=24)

# Use when:
# - Data is relatively stationary
# - Need fast predictions
# - Simple patterns
```

**Prophet**:
```python
# Business metrics with seasonality
from prophet import Prophet

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True
)
model.fit(df)
forecast = model.predict(future)

# Use when:
# - Strong seasonality
# - Holiday effects
# - Business KPIs
# - Need uncertainty intervals
```

**LSTM**:
```python
# Complex, non-linear patterns
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

model = Sequential([
    LSTM(50, activation='relu', input_shape=(n_steps, n_features)),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse')

# Use when:
# - Complex dependencies
# - Large dataset available
# - Non-stationary patterns
# - High accuracy required
```

---

### Q3: How do you handle multi-variate time series forecasting for interdependent metrics?

**Answer:**

**Vector Autoregression (VAR)**:

```python
from statsmodels.tsa.vector_ar.var_model import VAR
import pandas as pd

def forecast_interdependent_metrics(data):
    """
    Forecast multiple correlated metrics simultaneously
    data: DataFrame with columns [cpu_usage, memory_usage, request_rate]
    """
    # Fit VAR model
    model = VAR(data)
    results = model.fit(maxlags=15)
    
    # Forecast
    forecast = results.forecast(data.values[-results.k_ar:], steps=24)
    
    forecast_df = pd.DataFrame(
        forecast,
        columns=data.columns
    )
    
    return forecast_df

# Example
metrics = pd.DataFrame({
    'cpu_usage': cpu_data,
    'memory_usage': memory_data,
    'request_rate': request_data
})

forecast = forecast_interdependent_metrics(metrics)
```

**Multi-Output LSTM**:

```python
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Concatenate

def build_multivariate_lstm(n_features, n_outputs):
    """Build LSTM for multiple correlated metrics"""
    input_layer = Input(shape=(n_timesteps, n_features))
    
    lstm1 = LSTM(100, return_sequences=True)(input_layer)
    lstm2 = LSTM(50)(lstm1)
    
    # Separate heads for each metric
    cpu_output = Dense(1, name='cpu')(lstm2)
    memory_output = Dense(1, name='memory')(lstm2)
    requests_output = Dense(1, name='requests')(lstm2)
    
    model = Model(
        inputs=input_layer,
        outputs=[cpu_output, memory_output, requests_output]
    )
    
    model.compile(
        optimizer='adam',
        loss={'cpu': 'mse', 'memory': 'mse', 'requests': 'mse'}
    )
    
    return model

# Usage
model = build_multivariate_lstm(n_features=10, n_outputs=3)
model.fit(X_train, [y_cpu, y_memory, y_requests])
```

---

## NLP for IT Operations

### Q4: How do you use NLP to automatically categorize incident tickets?

**Answer:**

**Full Pipeline**:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import re

class IncidentClassifier:
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )),
            ('classifier', MultinomialNB())
        ])
        
        self.categories = {
            'performance': ['slow', 'latency', 'timeout', 'lag'],
            'availability': ['down', 'unavailable', '503', 'outage'],
            'security': ['breach', 'unauthorized', 'malware', 'attack'],
            'capacity': ['disk full', 'out of memory', 'quota exceeded']
        }
    
    def preprocess(self, text):
        """Clean and normalize text"""
        # Lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\\S+|www\\S+', '', text)
        
        # Remove special chars but keep important ones
        text = re.sub(r'[^a-z0-9\\s\\-]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def train(self, tickets, labels):
        """Train classifier on historical tickets"""
        # Preprocess
        processed_tickets = [self.preprocess(t) for t in tickets]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            processed_tickets, labels,
            test_size=0.2,
            stratify=labels
        )
        
        # Train
        self.pipeline.fit(X_train, y_train)
        
        # Evaluate
        accuracy = self.pipeline.score(X_test, y_test)
        print(f"Classification Accuracy: {accuracy:.2%}")
        
        return self
    
    def classify(self, ticket_text):
        """Classify new incident"""
        processed = self.preprocess(ticket_text)
        
        # Predict category
        category = self.pipeline.predict([processed])[0]
        
        # Get confidence scores
        probabilities = self.pipeline.predict_proba([processed])[0]
        confidence = max(probabilities)
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(ticket_text)
        
        # Suggest similar resolved incidents
        similar_incidents = self._find_similar_incidents(ticket_text)
        
        return {
            'category': category,
            'confidence': confidence,
            'key_phrases': key_phrases,
            'similar_incidents': similar_incidents,
            'suggested_team': self._route_to_team(category)
        }
    
    def _extract_key_phrases(self, text):
        """Extract important phrases from ticket"""
        # Get TF-IDF scores
        tfidf_matrix = self.pipeline.named_steps['tfidf'].transform([text])
        feature_names = self.pipeline.named_steps['tfidf'].get_feature_names_out()
        
        # Get top scoring terms
        scores = tfidf_matrix.toarray()[0]
        top_indices = scores.argsort()[-5:][::-1]
        
        return [feature_names[i] for i in top_indices]
    
    def _find_similar_incidents(self, text):
        """Find similar resolved incidents"""
        # In production, use vector similarity search
        # Here's a simplified version
        return []  # Query incident database
    
    def _route_to_team(self, category):
        """Route to appropriate team"""
        routing = {
            'performance': 'Performance Engineering',
            'availability': 'SRE Team',
            'security': 'Security Team',
            'capacity': 'Infrastructure Team'
        }
        return routing.get(category, 'General Support')

# Usage
classifier = IncidentClassifier()

# Train on historical data
historical_tickets = [
    "Application is very slow for all users",
    "Service is down - returning 503 errors",
    "Suspicious login attempts detected",
    "Disk space at 98% on production server"
]

labels = ['performance', 'availability', 'security', 'capacity']

classifier.train(historical_tickets, labels)

# Classify new incident
new_ticket = "API response time increased to 5 seconds"
result = classifier.classify(new_ticket)

print(f"Category: {result['category']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Route to: {result['suggested_team']}")
```

---

### Q5: How do you extract structured information from unstructured log messages?

**Answer:**

**Named Entity Recognition (NER) for Logs**:

```python
import re
from typing import Dict, List
import spacy

class LogEntityExtractor:
    def __init__(self):
        # Patterns for common entities
        self.patterns = {
            'ip_address': r'\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b',
            'timestamp': r'\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}',
            'error_code': r'\\b[45]\\d{2}\\b',  # HTTP errors
            'duration_ms': r'(\\d+)ms',
            'user_id': r'user[_-]?id[:\"]?\\s*([a-zA-Z0-9-]+)',
            'service_name': r'service[:\"]?\\s*([a-zA-Z0-9-]+)',
            'request_id': r'request[_-]?id[:\"]?\\s*([a-zA-Z0-9-]+)'
        }
    
    def extract(self, log_message: str) -> Dict:
        """Extract structured data from log message"""
        entities = {}
        
        for entity_type, pattern in self.patterns.items():
            matches = re.findall(pattern, log_message, re.IGNORECASE)
            if matches:
                # Handle groups
                if isinstance(matches[0], tuple):
                    entities[entity_type] = [m for m in matches[0] if m]
                else:
                    entities[entity_type] = matches
        
        # Extract severity
        entities['severity'] = self._extract_severity(log_message)
        
        # Extract message text (cleaned)
        entities['message'] = self._extract_message(log_message)
        
        # Classify error type
        entities['error_type'] = self._classify_error(log_message)
        
        return entities
    
    def _extract_severity(self, log_message: str) -> str:
        """Extract log level"""
        levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
        for level in levels:
            if level in log_message.upper():
                return level
        return 'UNKNOWN'
    
    def _extract_message(self, log_message: str) -> str:
        """Extract human-readable message"""
        # Remove timestamp, level, metadata
        cleaned = re.sub(r'^\\S+\\s+\\S+\\s+', '', log_message)
        cleaned = re.sub(r'\\[.*?\\]', '', cleaned)
        return cleaned.strip()
    
    def _classify_error(self, log_message: str) -> str:
        """Classify type of error"""
        if re.search(r'timeout|timed out', log_message, re.I):
            return 'timeout'
        elif re.search(r'connection.*refused|cannot connect', log_message, re.I):
            return 'connection_error'
        elif re.search(r'out of memory|oom', log_message, re.I):
            return 'memory_error'
        elif re.search(r'permission denied|unauthorized', log_message, re.I):
            return 'auth_error'
        elif re.search(r'not found|404', log_message, re.I):
            return 'not_found'
        else:
            return 'unknown'

    def batch_extract(self, log_lines: List[str]) -> List[Dict]:
        """Extract entities from multiple log lines"""
        return [self.extract(line) for line in log_lines]
    
    def summarize_logs(self, extracted_entities: List[Dict]) -> Dict:
        """Summarize extracted information"""
        from collections import Counter
        
        summary = {
            'total_logs': len(extracted_entities),
            'severity_distribution': Counter(e.get('severity') for e in extracted_entities),
            'error_type_distribution': Counter(e.get('error_type') for e in extracted_entities),
            'top_services': Counter(
                s for e in extracted_entities 
                for s in e.get('service_name', [])
            ).most_common(10),
            'unique_users': len(set(
                u for e in extracted_entities 
                for u in e.get('user_id', [])
            ))
        }
        
        return summary

# Usage
extractor = LogEntityExtractor()

log_lines = [
    "2026-07-14T10:00:00 ERROR [api-gateway] Request timeout: user_id=user-123 request_id=req-456 duration=5000ms ip=192.168.1.100",
    "2026-07-14T10:00:15 ERROR [payment-service] Connection refused to database service=payment-db",
    "2026-07-14T10:00:30 WARNING [auth-service] Failed login attempt user_id=user-789 ip=203.0.113.42"
]

# Extract from all logs
extracted = extractor.batch_extract(log_lines)

for entity_data in extracted:
    print(f"Severity: {entity_data['severity']}")
    print(f"Error Type: {entity_data['error_type']}")
    print(f"Entities: {entity_data}")
    print()

# Get summary
summary = extractor.summarize_logs(extracted)
print("Summary:", summary)
```

---

## Graph Analytics for RCA

### Q6: How do you use graph neural networks for root cause analysis in microservices?

**Answer:**

**Graph-Based RCA System**:

```python
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple

class GraphBasedRCA:
    def __init__(self):
        self.service_graph = nx.DiGraph()
        self.anomaly_history = []
    
    def build_service_graph(self, dependencies: List[Tuple[str, str]]):
        """Build dependency graph from service relationships"""
        self.service_graph.clear()
        
        for upstream, downstream in dependencies:
            self.service_graph.add_edge(upstream, downstream)
        
        # Calculate service importance using PageRank
        self.service_importance = nx.pagerank(self.service_graph)
    
    def record_anomaly(self, service: str, metric: str, 
                      timestamp: float, severity: float):
        """Record service anomaly"""
        self.anomaly_history.append({
            'service': service,
            'metric': metric,
            'timestamp': timestamp,
            'severity': severity
        })
    
    def identify_root_cause(self, time_window: int = 300) -> Dict:
        """Identify root cause using graph propagation"""
        if not self.anomaly_history:
            return None
        
        # Get recent anomalies within time window
        recent_time = max(a['timestamp'] for a in self.anomaly_history)
        recent_anomalies = [
            a for a in self.anomaly_history
            if recent_time - a['timestamp'] <= time_window
        ]
        
        # Calculate propagation scores
        propagation_scores = {}
        
        for anomaly in recent_anomalies:
            service = anomaly['service']
            
            if service not in propagation_scores:
                propagation_scores[service] = 0
            
            # Base score from severity
            score = anomaly['severity']
            
            # Boost score for upstream services (potential root causes)
            downstream_count = len(list(self.service_graph.successors(service)))
            score *= (1 + downstream_count * 0.2)
            
            # Boost score for important services (PageRank)
            importance = self.service_importance.get(service, 0)
            score *= (1 + importance)
            
            # Boost score for earlier anomalies
            time_factor = 1 + (recent_time - anomaly['timestamp']) / time_window
            score *= time_factor
            
            propagation_scores[service] = max(
                propagation_scores[service],
                score
            )
        
        # Identify root cause (highest score)
        root_cause_service = max(
            propagation_scores.items(),
            key=lambda x: x[1]
        )[0]
        
        # Find affected downstream services
        affected_services = list(nx.descendants(
            self.service_graph,
            root_cause_service
        ))
        
        # Calculate confidence
        total_anomalies = len(recent_anomalies)
        service_anomalies = sum(
            1 for a in recent_anomalies 
            if a['service'] == root_cause_service
        )
        confidence = service_anomalies / total_anomalies
        
        return {
            'root_cause': root_cause_service,
            'confidence': confidence,
            'affected_services': affected_services,
            'propagation_path': self._trace_propagation(root_cause_service),
            'evidence': [
                a for a in recent_anomalies 
                if a['service'] == root_cause_service
            ]
        }
    
    def _trace_propagation(self, root_service: str) -> List[List[str]]:
        """Trace how failure propagates through graph"""
        # Find all paths from root to affected services
        paths = []
        
        for descendant in nx.descendants(self.service_graph, root_service):
            try:
                path = nx.shortest_path(
                    self.service_graph,
                    root_service,
                    descendant
                )
                paths.append(path)
            except nx.NetworkXNoPath:
                continue
        
        return paths
    
    def visualize_rca(self, rca_result: Dict):
        """Visualize RCA result"""
        import matplotlib.pyplot as plt
        
        # Create subgraph with root cause and affected services
        nodes = [rca_result['root_cause']] + rca_result['affected_services']
        subgraph = self.service_graph.subgraph(nodes)
        
        # Color nodes
        node_colors = []
        for node in subgraph.nodes():
            if node == rca_result['root_cause']:
                node_colors.append('red')  # Root cause
            else:
                node_colors.append('orange')  # Affected
        
        # Draw graph
        pos = nx.spring_layout(subgraph)
        nx.draw(
            subgraph,
            pos,
            node_color=node_colors,
            with_labels=True,
            node_size=2000,
            font_size=10,
            arrows=True
        )
        
        plt.title(f"Root Cause: {rca_result['root_cause']}")
        plt.show()

# Usage
rca_engine = GraphBasedRCA()

# Build service dependency graph
dependencies = [
    ('api-gateway', 'auth-service'),
    ('api-gateway', 'user-service'),
    ('api-gateway', 'payment-service'),
    ('payment-service', 'database'),
    ('user-service', 'database'),
    ('auth-service', 'redis')
]

rca_engine.build_service_graph(dependencies)

# Record anomalies
import time
current_time = time.time()

rca_engine.record_anomaly('database', 'high_latency', current_time - 300, severity=0.9)
rca_engine.record_anomaly('payment-service', 'errors', current_time - 200, severity=0.7)
rca_engine.record_anomaly('user-service', 'errors', current_time - 180, severity=0.6)
rca_engine.record_anomaly('api-gateway', '503_errors', current_time - 100, severity=0.8)

# Identify root cause
result = rca_engine.identify_root_cause()

print(f"Root Cause: {result['root_cause']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Affected Services: {', '.join(result['affected_services'])}")
print(f"Propagation Paths: {result['propagation_path']}")
```

---

##
 Reinforcement Learning for Auto-Remediation

### Q7: How do you implement reinforcement learning for automated incident remediation?

**Answer:**

**RL-Based Remediation Agent**:

```python
import numpy as np
from collections import defaultdict, deque
import random

class RemediationAgent:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.95, 
                 epsilon=0.1):
        self.actions = actions  # Available remediation actions
        self.q_table = defaultdict(lambda: np.zeros(len(actions)))
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        
        self.history = deque(maxlen=1000)
    
    def get_state(self, incident):
        """Convert incident to state representation"""
        # Create state tuple from incident features
        state = (
            incident['service'],
            incident['metric'],
            self._discretize_severity(incident['severity']),
            self._discretize_duration(incident['duration']),
            incident.get('previous_action', 'none')
        )
        return state
    
    def _discretize_severity(self, severity):
        """Convert continuous severity to discrete bins"""
        if severity < 0.3:
            return 'low'
        elif severity < 0.7:
            return 'medium'
        else:
            return 'high'
    
    def _discretize_duration(self, duration):
        """Convert duration to discrete bins"""
        if duration < 300:  # 5 minutes
            return 'short'
        elif duration < 1800:  # 30 minutes
            return 'medium'
        else:
            return 'long'
    
    def select_action(self, state, training=True):
        """Select action using epsilon-greedy strategy"""
        if training and random.random() < self.epsilon:
            # Explore: random action
            return random.choice(self.actions)
        else:
            # Exploit: best known action
            q_values = self.q_table[state]
            max_q = np.max(q_values)
            
            # Handle ties by random selection
            best_actions = [i for i, q in enumerate(q_values) if q == max_q]
            action_idx = random.choice(best_actions)
            
            return self.actions[action_idx]
    
    def update_q_value(self, state, action, reward, next_state):
        """Update Q-value using Q-learning algorithm"""
        action_idx = self.actions.index(action)
        
        # Current Q-value
        current_q = self.q_table[state][action_idx]
        
        # Maximum Q-value for next state
        max_next_q = np.max(self.q_table[next_state])
        
        # Q-learning update
        new_q = current_q + self.lr * (
            reward + self.gamma * max_next_q - current_q
        )
        
        self.q_table[state][action_idx] = new_q
    
    def train_episode(self, incident, environment):
        """Train on one incident episode"""
        state = self.get_state(incident)
        action = self.select_action(state, training=True)
        
        # Execute action in environment
        result = environment.execute_action(action, incident)
        
        # Calculate reward
        reward = self._calculate_reward(result, incident)
        
        # Get next state
        next_incident = result.get('incident_state')
        next_state = self.get_state(next_incident) if next_incident else state
        
        # Update Q-value
        self.update_q_value(state, action, reward, next_state)
        
        # Record history
        self.history.append({
            'state': state,
            'action': action,
            'reward': reward,
            'result': result
        })
        
        return action, reward
    
    def _calculate_reward(self, result, incident):
        """Calculate reward for taken action"""
        reward = 0
        
        # Positive reward for resolving incident
        if result.get('resolved'):
            reward += 100
            
            # Bonus for quick resolution
            resolution_time = result.get('resolution_time', 0)
            if resolution_time < 300:  # < 5 minutes
                reward += 50
            elif resolution_time < 600:  # < 10 minutes
                reward += 25
        
        # Negative reward for failed action
        if result.get('failed'):
            reward -= 50
        
        # Penalty for service disruption during remediation
        if result.get('disruption'):
            reward -= 30
        
        # Penalty for human intervention needed
        if result.get('human_intervention'):
            reward -= 20
        
        # Bonus for cost-effective action
        action_cost = result.get('cost', 0)
        reward -= action_cost
        
        return reward
    
    def get_recommended_action(self, incident):
        """Get best action for production use"""
        state = self.get_state(incident)
        action = self.select_action(state, training=False)
        
        # Get confidence (Q-value normalized)
        action_idx = self.actions.index(action)
        q_values = self.q_table[state]
        confidence = q_values[action_idx] / (np.sum(np.abs(q_values)) + 1e-10)
        
        # Get alternative actions
        sorted_actions = sorted(
            enumerate(q_values),
            key=lambda x: x[1],
            reverse=True
        )
        
        alternatives = [
            {
                'action': self.actions[idx],
                'q_value': q_val
            }
            for idx, q_val in sorted_actions[1:4]
        ]
        
        return {
            'recommended_action': action,
            'confidence': confidence,
            'alternatives': alternatives,
            'state': state
        }
    
    def save_model(self, filepath):
        """Save trained Q-table"""
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(dict(self.q_table), f)
    
    def load_model(self, filepath):
        """Load trained Q-table"""
        import pickle
        with open(filepath, 'rb') as f:
            self.q_table = defaultdict(lambda: np.zeros(len(self.actions)), 
                                      pickle.load(f))

# Environment simulator
class RemediationEnvironment:
    def execute_action(self, action, incident):
        """Simulate action execution"""
        # In production, this would actually execute the remediation
        # For training, we simulate the outcome
        
        # Simplified simulation logic
        success_probability = {
            'restart_pod': 0.8,
            'scale_horizontal': 0.9,
            'clear_cache': 0.7,
            'rollback_deployment': 0.95,
            'increase_resources': 0.85
        }.get(action, 0.5)
        
        resolved = random.random() < success_probability
        
        return {
            'resolved': resolved,
            'failed': not resolved,
            'resolution_time': random.randint(60, 600) if resolved else 0,
            'disruption': action == 'restart_pod',
            'cost': self._calculate_action_cost(action),
            'incident_state': None if resolved else incident
        }
    
    def _calculate_action_cost(self, action):
        """Estimate cost of action"""
        costs = {
            'restart_pod': 1,
            'scale_horizontal': 5,
            'clear_cache': 1,
            'rollback_deployment': 3,
            'increase_resources': 10
        }
        return costs.get(action, 0)

# Usage
actions = [
    'restart_pod',
    'scale_horizontal',
    'clear_cache',
    'rollback_deployment',
    'increase_resources'
]

agent = RemediationAgent(actions)
environment = RemediationEnvironment()

# Training
print("Training agent...")
for episode in range(1000):
    # Simulate incident
    incident = {
        'service': random.choice(['api', 'database', 'cache']),
        'metric': random.choice(['cpu', 'memory', 'errors']),
        'severity': random.random(),
        'duration': random.randint(0, 3600)
    }
    
    action, reward = agent.train_episode(incident, environment)
    
    if episode % 100 == 0:
        avg_reward = np.mean([h['reward'] for h in list(agent.history)[-100:]])
        print(f"Episode {episode}, Avg Reward: {avg_reward:.2f}")

# Save model
agent.save_model('remediation_agent.pkl')

# Production use
new_incident = {
    'service': 'api',
    'metric': 'errors',
    'severity': 0.85,
    'duration': 120
}

recommendation = agent.get_recommended_action(new_incident)
print(f"\nIncident: {new_incident}")
print(f"Recommended Action: {recommendation['recommended_action']}")
print(f"Confidence: {recommendation['confidence']:.2%}")
```

---

## AIOps at Scale

### Q8: How do you scale AIOps to handle millions of metrics per second?

**Answer:**

**Scalable AIOps Architecture**:

```python
# 1. Data Sampling Strategy
class AdaptiveSampler:
    def __init__(self):
        self.sample_rates = defaultdict(lambda: 1.0)
    
    def should_process(self, metric_name, value, metadata):
        """Decide whether to process this data point"""
        # Always process errors
        if metadata.get('is_error'):
            return True
        
        # Always process anomalies
        if self._is_likely_anomaly(value, metric_name):
            return True
        
        # Sample based on metric importance
        sample_rate = self.sample_rates[metric_name]
        return random.random() < sample_rate
    
    def _is_likely_anomaly(self, value, metric_name):
        """Quick anomaly check"""
        # Use simple statistical bound
        stats = self._get_cached_stats(metric_name)
        if stats:
            z_score = abs((value - stats['mean']) / stats['std'])
            return z_score > 3
        return False

# 2. Distributed Processing with Apache Kafka + Flink
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer

def create_anomaly_detection_pipeline():
    """Create distributed anomaly detection pipeline"""
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(10)  # Scale workers
    
    # Kafka source
    kafka_consumer = FlinkKafkaConsumer(
        topics='metrics',
        deserialization_schema=JsonDeserializationSchema(),
        properties={'bootstrap.servers': 'kafka:9092'}
    )
    
    # Processing pipeline
    stream = env.add_source(kafka_consumer)
    
    # Window and detect
    anomalies = (stream
        .key_by(lambda x: x['metric_name'])
        .window(TumblingProcessingTimeWindows.of(Time.seconds(60)))
        .process(AnomalyDetectionFunction())
    )
    
    # Sink to alerts
    anomalies.add_sink(AlertingSink())
    
    env.execute("AIOps Anomaly Detection")

# 3. Hierarchical Aggregation
class MetricAggregator:
    def aggregate_metrics(self, raw_metrics):
        """Aggregate metrics at multiple levels"""
        aggregations = {
            # Service level
            'service': self._aggregate_by('service', raw_metrics),
            
            # Data center level
            'datacenter': self._aggregate_by('datacenter', raw_metrics),
            
            # Global level
            'global': self._aggregate_global(raw_metrics)
        }
        
        return aggregations
    
    def _aggregate_by(self, dimension, metrics):
        """Aggregate by dimension"""
        from collections import defaultdict
        
        groups = defaultdict(list)
        for metric in metrics:
            key = metric.get(dimension)
            groups[key].append(metric['value'])
        
        return {
            key: {
                'mean': np.mean(values),
                'p95': np.percentile(values, 95),
                'p99': np.percentile(values, 99),
                'max': np.max(values)
            }
            for key, values in groups.items()
        }

# 4. Model Sharding
class ShardedAnomalyDetector:
    def __init__(self, num_shards=10):
        self.num_shards = num_shards
        self.detectors = [
            IsolationForest(n_estimators=10)  # Smaller models
            for _ in range(num_shards)
        ]
    
    def get_shard(self, metric_name):
        """Deterministic shard selection"""
        return hash(metric_name) % self.num_shards
    
    def detect(self, metric_name, value):
        """Route to appropriate shard"""
        shard_id = self.get_shard(metric_name)
        detector = self.detectors[shard_id]
        return detector.predict([[value]])[0]

# 5. Caching Layer
import redis

class MetricsCache:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379)
        self.ttl = 300  # 5 minutes
    
    def get_baseline(self, metric_name):
        """Get cached baseline statistics"""
        key = f"baseline:{metric_name}"
        cached = self.redis.get(key)
        
        if cached:
            import json
            return json.loads(cached)
        
        return None
    
    def set_baseline(self, metric_name, stats):
        """Cache baseline statistics"""
        import json
        key = f"baseline:{metric_name}"
        self.redis.setex(key, self.ttl, json.dumps(stats))

# 6. Batch Processing for Training
class BatchModelTrainer:
    def train_models_batch(self, historical_data, batch_size=1000):
        """Train models in batches"""
        metrics = list(historical_data.keys())
        
        for i in range(0, len(metrics), batch_size):
            batch_metrics = metrics[i:i+batch_size]
            
            # Train models for this batch in parallel
            from multiprocessing import Pool
            
            with Pool(processes=8) as pool:
                results = pool.map(
                    self._train_single_model,
                    [(m, historical_data[m]) for m in batch_metrics]
                )
            
            # Save models
            for metric, model in results:
                self._save_model(metric, model)
```

**Scaling Strategies**:

1. **Sampling**: Process only important data
2. **Aggregation**: Reduce data volume
3. **Sharding**: Distribute models
4. **Caching**: Avoid repeated computations
5. **Batch Processing**: Efficient training
6. **Stream Processing**: Real-time analysis

**Performance Metrics**:
- Throughput: 10M+ metrics/second
- Latency: < 100ms for detection
- Storage: Compressed time-series DB
- Cost: Optimize for cloud efficiency

---

### Q9: How do you ensure AIOps model interpretability and explainability?

**Answer:**

**Explainable AI for AIOps**:

```python
import shap
from sklearn.ensemble import RandomForestClassifier
import lime
import lime.lime_tabular

class ExplainableAnomalyDetector:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.feature_names = None
        self.explainer = None
    
    def train(self, X, y, feature_names):
        """Train model and setup explainer"""
        self.feature_names = feature_names
        self.model.fit(X, y)
        
        # Setup SHAP explainer
        self.explainer = shap.TreeExplainer(self.model)
    
    def predict_with_explanation(self, X):
        """Predict and explain"""
        prediction = self.model.predict(X)
        
        # Get SHAP values
        shap_values = self.explainer.shap_values(X)
        
        # Feature importance for this prediction
        feature_importance = dict(zip(
            self.feature_names,
            shap_values[0]  # For first sample
        ))
        
        # Sort by absolute importance
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            prediction[0],
            sorted_features[:5]
        )
        
        return {
            'prediction': 'anomaly' if prediction[0] == 1 else 'normal',
            'confidence': self.model.predict_proba(X)[0][prediction[0]],
            'explanation': explanation,
            'top_features': sorted_features[:5],
            'shap_values': shap_values
        }
    
    def _generate_explanation(self, prediction, top_features):
        """Generate human-readable explanation"""
        if prediction == 1:  # Anomaly
            explanations = []
            for feature, importance in top_features:
                if importance > 0:
                    explanations.append(
                        f"{feature} is significantly higher than normal"
                    )
                else:
                    explanations.append(
                        f"{feature} is significantly lower than normal"
                    )
            
            return "Anomaly detected because: " + ", ".join(explanations)
        else:
            return "All metrics within normal ranges"
    
    def visualize_explanation(self, X):
        """Visualize SHAP explanation"""
        shap_values = self.explainer.shap_values(X)
        
        # Force plot for single prediction
        shap.force_plot(
            self.explainer.expected_value[1],
            shap_values[1][0],
            X[0],
            feature_names=self.feature_names
        )
        
        # Summary plot for dataset
        shap.summary_plot(
            shap_values[1],
            X,
            feature_names=self.feature_names
        )

# Usage
detector = ExplainableAnomalyDetector()

# Train
X_train = np.random.randn(1000, 5)
y_train = np.random.randint(0, 2, 1000)
feature_names = ['cpu', 'memory', 'latency', 'errors', 'requests']

detector.train(X_train, y_train, feature_names)

# Predict with explanation
X_new = np.array([[0.8, 0.9, 2.5, 100, 1000]])
result = detector.predict_with_explanation(X_new)

print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Explanation: {result['explanation']}")
print(f"\nTop Contributing Features:")
for feature, importance in result['top_features']:
    print(f"  {feature}: {importance:.3f}")
```

---

## Production Best Practices

### Q10: What are the key considerations for deploying AIOps in production?

**Answer:**

**1. Model Monitoring**:
```python
class ModelMonitor:
    def monitor_model_health(self, model, recent_data):
        """Monitor model performance in production"""
        metrics = {
            'prediction_latency': self._measure_latency(model, recent_data),
            'prediction_distribution': self._check_distribution(model, recent_data),
            'feature_drift': self._detect_feature_drift(recent_data),
            'model_accuracy': self._estimate_accuracy(model, recent_data)
        }
        
        # Alert if issues detected
        if any(self._is_degraded(m) for m in metrics.values()):
            self._trigger_alert(metrics)
        
        return metrics
```

**2. Gradual Rollout**:
```python
class CanaryDeployment:
    def deploy_new_model(self, new_model, traffic_percentage=10):
        """Gradually roll out new model"""
        # Route small percentage to new model
        # Monitor performance
        # Increase traffic if successful
        pass
```

**3. Human-in-the-Loop**:
```python
class HumanApprovalWorkflow:
    def execute_with_approval(self, action, incident):
        """Require human approval for critical actions"""
        if self._is_critical(action, incident):
            approval = self._request_approval(action, incident)
            if not approval:
                return {'status': 'rejected', 'reason': 'no_approval'}
        
        return self._execute_action(action, incident)
```

**4. Feedback Loop**:
```python
class FeedbackCollector:
    def collect_feedback(self, prediction_id, was_correct):
        """Collect feedback for model improvement"""
        self.feedback_db.insert({
            'prediction_id': prediction_id,
            'was_correct': was_correct,
            'timestamp': datetime.now()
        })
        
        # Trigger retraining if needed
        if self._should_retrain():
            self._schedule_retraining()
```

**5. Disaster Recovery**:
```python
class AIOpsFailover:
    def handle_model_failure(self):
        """Fallback to rule-based system if AI fails"""
        if not self.model_healthy():
            self.switch_to_fallback()
            self.alert_team()
```

---

## Summary

Key takeaways for advanced AIOps:

✅ Use appropriate time series models (ARIMA/Prophet/LSTM)  
✅ Apply NLP for log analysis and incident classification  
✅ Leverage graph analytics for complex RCA  
✅ Implement RL for intelligent auto-remediation  
✅ Design for scale (sampling, sharding, caching)  
✅ Ensure model interpretability  
✅ Monitor AI systems themselves  
✅ Maintain human oversight  
✅ Implement feedback loops  
✅ Plan for failure scenarios  

---

**Congratulations!** You've completed the advanced AIOps interview questions. You're now ready for senior AIOps engineering roles.

**Next Steps**:
- Complete the [Real-World AIOps Project](20-real-world-aiops-project.md)
- Practice with hands-on labs
- Build your own AIOps portfolio

---

**Previous**: [Intermediate Questions](../02-intermediate/interview-questions-intermediate.md)  
**Next**: [Real-World Project](20-real-world-aiops-project.md)
