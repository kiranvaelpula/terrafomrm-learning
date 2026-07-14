# NLP for IT Operations

## Learning Objectives
- Apply Natural Language Processing to IT operations
- Process unstructured logs and tickets
- Extract insights from operational text
- Automate incident classification

---

## Why NLP in AIOps?

IT operations generate massive amounts of unstructured text:
- Log messages
- Incident tickets
- Chat conversations
- Documentation
- Runbooks

**NLP enables:**
- Automatic incident categorization
- Similar incident detection
- Knowledge extraction
- Chatbot assistance
- Root cause extraction from logs

---

## Text Processing Pipeline

```python
import spacy
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class ITOpsNLPProcessor:
    """NLP processor for IT operations text"""
    
    def __init__(self):
        # Load spaCy model
        self.nlp = spacy.load('en_core_web_sm')
        self.vectorizer = TfidfVectorizer(max_features=1000)
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove IPs
        text = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 'IP_ADDRESS', text)
        
        # Remove UUIDs
        text = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 
                     'UUID', text, flags=re.IGNORECASE)
        
        # Remove timestamps
        text = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', 'TIMESTAMP', text)
        
        # Remove numbers
        text = re.sub(r'\d+', 'NUM', text)
        
        return text
    
    def extract_entities(self, text):
        """Extract named entities"""
        
        doc = self.nlp(text)
        
        entities = {
            'services': [],
            'errors': [],
            'actions': [],
            'locations': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                entities['services'].append(ent.text)
            elif ent.label_ == 'GPE':
                entities['locations'].append(ent.text)
        
        # Extract error patterns
        error_patterns = [
            'error', 'failed', 'timeout', 'exception',
            'crashed', 'down', 'unavailable'
        ]
        
        for token in doc:
            if token.lemma_ in error_patterns:
                entities['errors'].append(token.text)
        
        return entities
    
    def extract_key_phrases(self, text):
        """Extract key phrases using noun chunks"""
        
        doc = self.nlp(text)
        
        key_phrases = []
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:  # Multi-word phrases
                key_phrases.append(chunk.text)
        
        return key_phrases

# Usage
processor = ITOpsNLPProcessor()

log_message = "2024-01-15 10:30:45 ERROR [payment-service] Transaction abc-123 failed: Connection timeout to database at 192.168.1.100"

cleaned = processor.preprocess_text(log_message)
entities = processor.extract_entities(log_message)
phrases = processor.extract_key_phrases(log_message)

print(f"Cleaned: {cleaned}")
print(f"Entities: {entities}")
print(f"Key phrases: {phrases}")
```

---

## Incident Classification

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd

class IncidentClassifier:
    """Classify incidents automatically"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
        self.classifier = RandomForestClassifier(n_estimators=100)
        self.categories = []
    
    def train(self, incidents_df):
        """Train classifier on historical incidents"""
        
        # Preprocess text
        processor = ITOpsNLPProcessor()
        incidents_df['cleaned_text'] = incidents_df['description'].apply(
            processor.preprocess_text
        )
        
        # Vectorize
        X = self.vectorizer.fit_transform(incidents_df['cleaned_text'])
        y = incidents_df['category']
        
        self.categories = y.unique().tolist()
        
        # Split and train
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.classifier.fit(X_train, y_train)
        
        # Evaluate
        accuracy = self.classifier.score(X_test, y_test)
        print(f"Classification accuracy: {accuracy:.2%}")
        
        return accuracy
    
    def classify(self, incident_text):
        """Classify new incident"""
        
        processor = ITOpsNLPProcessor()
        cleaned = processor.preprocess_text(incident_text)
        
        X = self.vectorizer.transform([cleaned])
        
        # Predict category
        category = self.classifier.predict(X)[0]
        
        # Get confidence
        probabilities = self.classifier.predict_proba(X)[0]
        confidence = probabilities.max()
        
        # Get top 3 categories
        top_indices = probabilities.argsort()[-3:][::-1]
        top_categories = [
            {
                'category': self.categories[i],
                'probability': probabilities[i]
            }
            for i in top_indices
        ]
        
        return {
            'category': category,
            'confidence': confidence,
            'top_categories': top_categories
        }
    
    def suggest_assignment(self, incident_text):
        """Suggest team assignment based on category"""
        
        classification = self.classify(incident_text)
        
        # Map categories to teams
        team_mapping = {
            'database': 'DBA Team',
            'network': 'Network Team',
            'application': 'App Team',
            'infrastructure': 'Infrastructure Team',
            'security': 'Security Team'
        }
        
        team = team_mapping.get(classification['category'], 'General Support')
        
        return {
            'category': classification['category'],
            'assigned_team': team,
            'confidence': classification['confidence']
        }

# Usage
classifier = IncidentClassifier()

# Train on historical data
historical_incidents = pd.DataFrame({
    'description': [
        "Database connection pool exhausted",
        "Network latency increased in us-east-1",
        "Application throwing null pointer exception",
        "Disk usage at 95% on server01"
    ],
    'category': ['database', 'network', 'application', 'infrastructure']
})

classifier.train(historical_incidents)

# Classify new incident
new_incident = "Unable to connect to MySQL database: timeout after 30 seconds"
result = classifier.classify(new_incident)

print(f"Category: {result['category']} ({result['confidence']:.1%} confidence)")
```

---

## Similar Incident Detection

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SimilarIncidentFinder:
    """Find similar historical incidents"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=300)
        self.incident_vectors = None
        self.incidents = []
    
    def index_incidents(self, incidents):
        """Index historical incidents"""
        
        self.incidents = incidents
        
        # Vectorize descriptions
        descriptions = [inc['description'] for inc in incidents]
        self.incident_vectors = self.vectorizer.fit_transform(descriptions)
        
        print(f"Indexed {len(incidents)} incidents")
    
    def find_similar(self, query_text, top_k=5, threshold=0.3):
        """Find similar incidents"""
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query_text])
        
        # Calculate similarity
        similarities = cosine_similarity(query_vector, self.incident_vectors)[0]
        
        # Get top k
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        similar_incidents = []
        for idx in top_indices:
            if similarities[idx] >= threshold:
                similar_incidents.append({
                    'incident': self.incidents[idx],
                    'similarity': similarities[idx]
                })
        
        return similar_incidents
    
    def suggest_solution(self, query_text):
        """Suggest solution based on similar incidents"""
        
        similar = self.find_similar(query_text, top_k=3)
        
        if not similar:
            return {
                'found_similar': False,
                'message': 'No similar incidents found'
            }
        
        # Get most similar resolved incident
        best_match = similar[0]
        
        if best_match['incident'].get('resolution'):
            return {
                'found_similar': True,
                'similarity': best_match['similarity'],
                'similar_incident': best_match['incident']['description'],
                'suggested_solution': best_match['incident']['resolution'],
                'resolved_by': best_match['incident'].get('resolved_by', 'Unknown')
            }
        
        return {
            'found_similar': True,
            'similarity': best_match['similarity'],
            'message': 'Similar incident found but no resolution documented'
        }

# Usage
finder = SimilarIncidentFinder()

# Index historical incidents
historical = [
    {
        'id': 1,
        'description': 'Payment service database connection timeout',
        'resolution': 'Increased connection pool size from 10 to 20',
        'resolved_by': 'DBA Team'
    },
    {
        'id': 2,
        'description': 'API gateway high latency',
        'resolution': 'Scaled replicas from 3 to 5',
        'resolved_by': 'Platform Team'
    }
]

finder.index_incidents(historical)

# Find similar for new incident
new_issue = "Payment API experiencing database timeout errors"
suggestion = finder.suggest_solution(new_issue)

if suggestion['found_similar']:
    print(f"Similar incident ({suggestion['similarity']:.1%} match):")
    print(f"Solution: {suggestion['suggested_solution']}")
```

---

## Log Pattern Mining

```python
from collections import Counter
import re

class LogPatternMiner:
    """Extract patterns from logs using NLP"""
    
    def __init__(self):
        self.patterns = []
    
    def extract_log_template(self, log_message):
        """Extract template from log message"""
        
        # Replace variables with placeholders
        template = log_message
        
        # Replace numbers
        template = re.sub(r'\d+', '<NUM>', template)
        
        # Replace IPs
        template = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '<IP>', template)
        
        # Replace timestamps
        template = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}', '<TIMESTAMP>', template)
        
        # Replace UUIDs
        template = re.sub(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}', 
                         '<UUID>', template, flags=re.IGNORECASE)
        
        # Replace paths
        template = re.sub(r'/[\w/]+', '<PATH>', template)
        
        return template
    
    def mine_patterns(self, log_messages):
        """Mine common patterns from logs"""
        
        # Extract templates
        templates = [self.extract_log_template(msg) for msg in log_messages]
        
        # Count occurrences
        template_counts = Counter(templates)
        
        # Store patterns
        self.patterns = [
            {
                'template': template,
                'count': count,
                'frequency': count / len(log_messages)
            }
            for template, count in template_counts.most_common()
        ]
        
        return self.patterns
    
    def identify_anomalous_logs(self, log_messages):
        """Identify logs that don't match known patterns"""
        
        if not self.patterns:
            raise ValueError("No patterns mined yet. Call mine_patterns first.")
        
        known_templates = {p['template'] for p in self.patterns}
        
        anomalous = []
        for msg in log_messages:
            template = self.extract_log_template(msg)
            
            if template not in known_templates:
                anomalous.append({
                    'message': msg,
                    'template': template
                })
        
        return anomalous

# Usage
miner = LogPatternMiner()

logs = [
    "2024-01-15 10:00:00 INFO User 123 logged in from 192.168.1.1",
    "2024-01-15 10:00:01 INFO User 456 logged in from 192.168.1.2",
    "2024-01-15 10:00:02 ERROR Failed to connect to database at 192.168.1.100",
    "2024-01-15 10:00:03 ERROR Failed to connect to database at 192.168.1.100",
    "2024-01-15 10:00:04 WARN High memory usage: 85%"
]

patterns = miner.mine_patterns(logs)

print("Common log patterns:")
for pattern in patterns[:5]:
    print(f"  {pattern['template']} (count: {pattern['count']})")
```

---

## Chatbot for IT Operations

```python
from transformers import pipeline
import torch

class ITOpsChatbot:
    """AI chatbot for IT operations assistance"""
    
    def __init__(self):
        # Use pre-trained QA model
        self.qa_pipeline = pipeline(
            "question-answering",
            model="distilbert-base-cased-distilled-squad"
        )
        
        self.knowledge_base = self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load operational knowledge"""
        
        return {
            'restart_service': """
            To restart a service:
            1. Check service status: systemctl status service-name
            2. Stop service: systemctl stop service-name
            3. Start service: systemctl start service-name
            4. Verify: systemctl status service-name
            """,
            
            'check_disk_space': """
            To check disk space:
            1. df -h to see all filesystems
            2. du -sh /path/* to see directory sizes
            3. Clean up with: rm old files or docker system prune
            """,
            
            'database_slow': """
            For slow database queries:
            1. Check running queries: SHOW FULL PROCESSLIST
            2. Check slow query log
            3. Add indexes if needed
            4. Optimize query
            5. Consider connection pool settings
            """
        }
    
    def answer_question(self, question, context=None):
        """Answer operational question"""
        
        if not context:
            # Find relevant context from knowledge base
            context = self.find_relevant_context(question)
        
        if not context:
            return {
                'answer': "I don't have information about that. Please consult the documentation.",
                'confidence': 0.0
            }
        
        # Use QA model
        result = self.qa_pipeline(question=question, context=context)
        
        return {
            'answer': result['answer'],
            'confidence': result['score']
        }
    
    def find_relevant_context(self, question):
        """Find relevant knowledge base entry"""
        
        question_lower = question.lower()
        
        keywords = {
            'restart': 'restart_service',
            'disk': 'check_disk_space',
            'slow query': 'database_slow',
            'database': 'database_slow'
        }
        
        for keyword, kb_key in keywords.items():
            if keyword in question_lower:
                return self.knowledge_base[kb_key]
        
        return None
    
    def suggest_runbook(self, incident_description):
        """Suggest relevant runbook"""
        
        # Classify incident type
        incident_type = self.classify_incident_type(incident_description)
        
        runbooks = {
            'service_down': 'Service Restart Runbook',
            'high_latency': 'Performance Troubleshooting Runbook',
            'disk_full': 'Disk Cleanup Runbook',
            'database_slow': 'Database Performance Runbook'
        }
        
        return runbooks.get(incident_type, 'General Troubleshooting Guide')
    
    def classify_incident_type(self, description):
        """Simple incident type classification"""
        
        desc_lower = description.lower()
        
        if 'down' in desc_lower or 'unavailable' in desc_lower:
            return 'service_down'
        elif 'slow' in desc_lower or 'latency' in desc_lower:
            return 'high_latency'
        elif 'disk' in desc_lower and 'full' in desc_lower:
            return 'disk_full'
        elif 'database' in desc_lower and 'slow' in desc_lower:
            return 'database_slow'
        
        return 'unknown'

# Usage
chatbot = ITOpsChatbot()

# Ask question
question = "How do I restart a service?"
answer = chatbot.answer_question(question)

print(f"Q: {question}")
print(f"A: {answer['answer']} (confidence: {answer['confidence']:.2%})")

# Suggest runbook
incident = "Database queries are running very slow"
runbook = chatbot.suggest_runbook(incident)
print(f"\nSuggested runbook: {runbook}")
```

---

## Summary

NLP in AIOps enables:
- Automated incident classification
- Similar incident detection
- Log pattern extraction
- Chatbot assistance
- Knowledge extraction

**Key techniques:**
- Text preprocessing
- Named entity recognition
- Text classification
- Similarity search
- Pattern mining

---

**Next**: [Graph Analytics →](15-graph-analytics.md)
