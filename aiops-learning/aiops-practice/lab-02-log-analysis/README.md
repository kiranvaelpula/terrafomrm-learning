# Lab 02: Intelligent Log Analysis with NLP

## Overview
Build a log analysis system using Natural Language Processing to automatically parse, categorize, and extract insights from application logs.

**Duration:** 2-3 hours  
**Difficulty:** Intermediate  
**Prerequisites:** Lab 01, Python, basic NLP knowledge

## Learning Objectives
- Parse and normalize unstructured logs
- Use NLP for log classification
- Extract entities and patterns from log messages
- Implement log clustering for pattern detection
- Build a simple log search interface

## Lab Architecture

```
Log Sources → Log Parser → NLP Processor → Pattern Detector → Insights Dashboard
                  ↓              ↓              ↓
              Normalizer    Classifier      Clustering
```

## Setup

### 1. Create Project Structure

```bash
mkdir -p lab-02-log-analysis/{data,notebooks,src}
cd lab-02-log-analysis
```

### 2. Install Dependencies

```bash
pip install pandas numpy scikit-learn \
    spacy nltk transformers \
    elasticsearch flask plotly
python -m spacy download en_core_web_sm
```

### 3. Sample Log Data

Create `data/sample_logs.txt`:

```
2024-01-15 10:23:45 ERROR [AuthService] Failed login attempt for user john@example.com from IP 192.168.1.100
2024-01-15 10:24:12 INFO [APIGateway] Request processed successfully - endpoint /api/users - latency 45ms
2024-01-15 10:24:30 WARN [DatabasePool] Connection pool reaching capacity - 85% utilized
2024-01-15 10:25:01 ERROR [PaymentService] Transaction failed - card declined - amount $150.00 - merchant_id 12345
2024-01-15 10:25:15 INFO [CacheService] Cache hit ratio 92% - avg response time 5ms
2024-01-15 10:26:00 CRITICAL [DatabaseCluster] Node db-node-02 unreachable - failover initiated
2024-01-15 10:26:45 ERROR [AuthService] Failed login attempt for user admin@example.com from IP 10.0.0.50
2024-01-15 10:27:10 INFO [LoadBalancer] Health check passed for all 5 backend instances
```

## Implementation

### Step 1: Log Parser

Create `src/log_parser.py`:

```python
import re
from datetime import datetime
from typing import Dict, List
import pandas as pd

class LogParser:
    def __init__(self):
        # Define log pattern
        self.pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\w+)\s+\[([\w]+)\]\s+(.*)'
        
    def parse_log_line(self, line: str) -> Dict:
        """Parse a single log line into structured format"""
        match = re.match(self.pattern, line.strip())
        
        if match:
            timestamp, level, service, message = match.groups()
            return {
                'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                'level': level,
                'service': service,
                'message': message,
                'raw_log': line
            }
        return None
    
    def parse_log_file(self, filepath: str) -> pd.DataFrame:
        """Parse entire log file"""
        logs = []
        with open(filepath, 'r') as f:
            for line in f:
                parsed = self.parse_log_line(line)
                if parsed:
                    logs.append(parsed)
        
        return pd.DataFrame(logs)
    
    def extract_entities(self, message: str) -> Dict:
        """Extract key entities from log message"""
        entities = {
            'ip_addresses': re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', message),
            'emails': re.findall(r'\b[\w.-]+@[\w.-]+\.\w+\b', message),
            'amounts': re.findall(r'\$\d+\.?\d*', message),
            'percentages': re.findall(r'\d+%', message),
            'latency': re.findall(r'\d+ms', message),
            'endpoints': re.findall(r'/[\w/]+', message)
        }
        return {k: v for k, v in entities.items() if v}

# Test the parser
if __name__ == "__main__":
    parser = LogParser()
    
    # Parse sample log
    log_line = "2024-01-15 10:23:45 ERROR [AuthService] Failed login attempt for user john@example.com from IP 192.168.1.100"
    parsed = parser.parse_log_line(log_line)
    print("Parsed log:", parsed)
    
    # Extract entities
    entities = parser.extract_entities(parsed['message'])
    print("Entities:", entities)
```

### Step 2: NLP-Based Log Classifier

Create `src/log_classifier.py`:

```python
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np

class LogClassifier:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.classifier = MultinomialNB()
        self.categories = []
        
    def preprocess_text(self, text: str) -> str:
        """Preprocess log message with spaCy"""
        doc = self.nlp(text.lower())
        # Remove stop words and keep only important tokens
        tokens = [token.lemma_ for token in doc 
                 if not token.is_stop and not token.is_punct]
        return ' '.join(tokens)
    
    def train(self, messages: List[str], categories: List[str]):
        """Train classifier on labeled logs"""
        # Preprocess messages
        processed = [self.preprocess_text(msg) for msg in messages]
        
        # Vectorize
        X = self.vectorizer.fit_transform(processed)
        
        # Train classifier
        self.classifier.fit(X, categories)
        self.categories = list(set(categories))
        
    def predict(self, message: str) -> str:
        """Classify a log message"""
        processed = self.preprocess_text(message)
        X = self.vectorizer.transform([processed])
        prediction = self.classifier.predict(X)
        probability = self.classifier.predict_proba(X).max()
        
        return {
            'category': prediction[0],
            'confidence': float(probability)
        }
    
    def categorize_logs(self, df):
        """Add category predictions to dataframe"""
        df['category'] = df['message'].apply(
            lambda x: self.predict(x)['category']
        )
        df['confidence'] = df['message'].apply(
            lambda x: self.predict(x)['confidence']
        )
        return df

# Train with sample data
if __name__ == "__main__":
    classifier = LogClassifier()
    
    # Training data
    training_messages = [
        "Failed login attempt for user",
        "Database connection timeout",
        "API request successful",
        "Memory usage exceeded threshold",
        "Authentication token expired",
        "Service health check passed"
    ]
    
    training_categories = [
        "security", "database", "api", 
        "performance", "security", "health"
    ]
    
    classifier.train(training_messages, training_categories)
    
    # Test prediction
    test_message = "Failed login from suspicious IP address"
    result = classifier.predict(test_message)
    print(f"Category: {result['category']}, Confidence: {result['confidence']:.2f}")
```

### Step 3: Log Pattern Detection

Create `src/pattern_detector.py`:

```python
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from collections import Counter

class PatternDetector:
    def __init__(self, eps=0.5, min_samples=2):
        self.vectorizer = TfidfVectorizer(max_features=50)
        self.clusterer = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        
    def detect_patterns(self, messages: List[str]) -> Dict:
        """Detect common patterns in log messages"""
        # Vectorize messages
        X = self.vectorizer.fit_transform(messages)
        
        # Cluster similar messages
        clusters = self.clusterer.fit_predict(X.toarray())
        
        # Analyze clusters
        patterns = {}
        for cluster_id in set(clusters):
            if cluster_id == -1:  # Noise
                continue
                
            cluster_messages = [msg for msg, cid in zip(messages, clusters) 
                              if cid == cluster_id]
            
            patterns[f"pattern_{cluster_id}"] = {
                'count': len(cluster_messages),
                'sample_messages': cluster_messages[:3],
                'frequency': len(cluster_messages) / len(messages)
            }
        
        return patterns
    
    def find_anomalous_logs(self, messages: List[str]) -> List[str]:
        """Find logs that don't match common patterns"""
        X = self.vectorizer.fit_transform(messages)
        clusters = self.clusterer.fit_predict(X.toarray())
        
        # Return messages in noise cluster
        anomalous = [msg for msg, cid in zip(messages, clusters) if cid == -1]
        return anomalous
    
    def extract_common_tokens(self, messages: List[str], top_n=10) -> List:
        """Extract most common tokens across messages"""
        all_tokens = []
        for msg in messages:
            tokens = msg.lower().split()
            all_tokens.extend(tokens)
        
        return Counter(all_tokens).most_common(top_n)

# Example usage
if __name__ == "__main__":
    detector = PatternDetector()
    
    sample_logs = [
        "Failed login attempt for user john",
        "Failed login attempt for user jane",
        "Failed login attempt for user admin",
        "API request successful for endpoint /users",
        "API request successful for endpoint /orders",
        "Database connection pool exhausted",
    ]
    
    patterns = detector.detect_patterns(sample_logs)
    print("Detected Patterns:")
    for pattern_id, info in patterns.items():
        print(f"\n{pattern_id}:")
        print(f"  Count: {info['count']}")
        print(f"  Frequency: {info['frequency']:.2%}")
        print(f"  Samples: {info['sample_messages']}")
    
    anomalies = detector.find_anomalous_logs(sample_logs)
    print(f"\nAnomalous logs: {anomalies}")
```

### Step 4: Complete Analysis Pipeline

Create `src/log_analyzer.py`:

```python
import pandas as pd
from log_parser import LogParser
from log_classifier import LogClassifier
from pattern_detector import PatternDetector

class LogAnalyzer:
    def __init__(self):
        self.parser = LogParser()
        self.classifier = LogClassifier()
        self.pattern_detector = PatternDetector()
        
    def analyze_logs(self, log_file: str) -> Dict:
        """Complete log analysis pipeline"""
        print("📊 Starting log analysis...")
        
        # 1. Parse logs
        print("1️⃣ Parsing logs...")
        df = self.parser.parse_log_file(log_file)
        print(f"   Parsed {len(df)} log entries")
        
        # 2. Extract entities
        print("2️⃣ Extracting entities...")
        df['entities'] = df['message'].apply(self.parser.extract_entities)
        
        # 3. Detect patterns
        print("3️⃣ Detecting patterns...")
        patterns = self.pattern_detector.detect_patterns(df['message'].tolist())
        
        # 4. Find anomalies
        print("4️⃣ Finding anomalies...")
        anomalies = self.pattern_detector.find_anomalous_logs(df['message'].tolist())
        
        # 5. Generate statistics
        print("5️⃣ Generating statistics...")
        stats = {
            'total_logs': len(df),
            'log_levels': df['level'].value_counts().to_dict(),
            'services': df['service'].value_counts().to_dict(),
            'time_range': {
                'start': df['timestamp'].min(),
                'end': df['timestamp'].max()
            },
            'patterns': patterns,
            'anomaly_count': len(anomalies),
            'anomalies': anomalies[:5]  # Top 5 anomalies
        }
        
        return {
            'dataframe': df,
            'statistics': stats
        }
    
    def generate_report(self, results: Dict):
        """Generate analysis report"""
        stats = results['statistics']
        
        print("\n" + "="*60)
        print("📋 LOG ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n📈 Overview:")
        print(f"   Total Logs: {stats['total_logs']}")
        print(f"   Time Range: {stats['time_range']['start']} to {stats['time_range']['end']}")
        
        print(f"\n🎯 Log Levels:")
        for level, count in stats['log_levels'].items():
            print(f"   {level}: {count}")
        
        print(f"\n🔧 Top Services:")
        for service, count in list(stats['services'].items())[:5]:
            print(f"   {service}: {count}")
        
        print(f"\n🔍 Detected Patterns: {len(stats['patterns'])}")
        for pattern_id, info in list(stats['patterns'].items())[:3]:
            print(f"   {pattern_id}: {info['count']} occurrences ({info['frequency']:.1%})")
        
        print(f"\n⚠️ Anomalies Found: {stats['anomaly_count']}")
        for anomaly in stats['anomalies']:
            print(f"   - {anomaly[:80]}...")
        
        print("\n" + "="*60)

# Run analysis
if __name__ == "__main__":
    analyzer = LogAnalyzer()
    
    # Analyze log file
    results = analyzer.analyze_logs('../data/sample_logs.txt')
    
    # Generate report
    analyzer.generate_report(results)
    
    # Save results
    results['dataframe'].to_csv('../data/analyzed_logs.csv', index=False)
    print("\n✅ Results saved to analyzed_logs.csv")
```

### Step 5: Interactive Dashboard

Create `src/dashboard.py`:

```python
from flask import Flask, render_template, jsonify
import pandas as pd
from log_analyzer import LogAnalyzer
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)
analyzer = LogAnalyzer()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/analyze')
def analyze():
    """Run analysis and return results"""
    results = analyzer.analyze_logs('../data/sample_logs.txt')
    stats = results['statistics']
    
    return jsonify({
        'total_logs': stats['total_logs'],
        'log_levels': stats['log_levels'],
        'services': stats['services'],
        'patterns': len(stats['patterns']),
        'anomalies': stats['anomaly_count']
    })

@app.route('/api/charts/log_levels')
def chart_log_levels():
    """Generate log level distribution chart"""
    results = analyzer.analyze_logs('../data/sample_logs.txt')
    df = results['dataframe']
    
    fig = px.pie(df, names='level', title='Log Level Distribution')
    return jsonify(fig.to_dict())

@app.route('/api/charts/timeline')
def chart_timeline():
    """Generate timeline chart"""
    results = analyzer.analyze_logs('../data/sample_logs.txt')
    df = results['dataframe']
    
    df['hour'] = df['timestamp'].dt.hour
    timeline = df.groupby(['hour', 'level']).size().reset_index(name='count')
    
    fig = px.line(timeline, x='hour', y='count', color='level',
                  title='Log Volume Over Time')
    return jsonify(fig.to_dict())

if __name__ == '__main__':
    print("🚀 Starting log analysis dashboard...")
    print("📊 Access at: http://localhost:5000")
    app.run(debug=True)
```

## Exercises

### Exercise 1: Enhanced Pattern Detection
Improve pattern detection to identify:
- Time-based patterns
- Correlation between different log types
- Cascading failures

### Exercise 2: Real-time Log Processing
Implement streaming log analysis:
```python
from kafka import KafkaConsumer

def process_log_stream():
    consumer = KafkaConsumer('logs')
    for message in consumer:
        log = parser.parse_log_line(message.value)
        category = classifier.predict(log['message'])
        # Process in real-time
```

### Exercise 3: Advanced NLP Features
Add advanced NLP capabilities:
- Named Entity Recognition for service names
- Sentiment analysis for error messages
- Intent classification

## Validation

Test your implementation:

```bash
# Run parser tests
python src/log_parser.py

# Run classifier tests
python src/log_classifier.py

# Run full analysis
python src/log_analyzer.py

# Start dashboard
python src/dashboard.py
```

## Key Takeaways

✅ Structured log parsing normalizes diverse log formats  
✅ NLP enables semantic understanding of log messages  
✅ Pattern detection reveals normal vs anomalous behavior  
✅ Entity extraction provides contextual insights  
✅ Real-time analysis supports proactive monitoring

## Next Steps

- **Lab 03**: Root Cause Analysis with graph-based correlation
- **Lab 04**: Predictive analytics for capacity planning
- Explore ELK stack integration
- Implement log retention policies

## Resources

- [Logstash Patterns](https://www.elastic.co/guide/en/logstash/current/plugins-filters-grok.html)
- [spaCy NLP](https://spacy.io/)
- [Log Analysis Best Practices](https://www.splunk.com/en_us/blog/learn/log-analysis.html)
