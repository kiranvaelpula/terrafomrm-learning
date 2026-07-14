# AIOps Security and Privacy

Learn how to build secure AIOps platforms that protect sensitive data, prevent attacks, and comply with regulations.

---

## Security Threats in AIOps

### 1. Data Poisoning Attacks

Attackers inject malicious data to corrupt ML models:

```python
# Example: Normal vs Poisoned Training Data

# Normal training data
normal_data = [
    {'cpu': 50, 'label': 'normal'},
    {'cpu': 55, 'label': 'normal'},
    {'cpu': 90, 'label': 'anomaly'},
]

# Poisoned data: Label anomalies as normal
poisoned_data = [
    {'cpu': 50, 'label': 'normal'},
    {'cpu': 55, 'label': 'normal'},
    {'cpu': 90, 'label': 'normal'},  # ← Should be anomaly!
]

# Model trained on poisoned data won't detect real anomalies
```

**Defense - Data Validation**:

```python
class DataValidator:
    def __init__(self):
        self.historical_stats = self.load_historical_stats()
    
    def validate_data_point(self, data):
        """Validate incoming data before training"""
        issues = []
        
        # Check for statistical outliers
        for feature, value in data.items():
            if feature in self.historical_stats:
                mean = self.historical_stats[feature]['mean']
                std = self.historical_stats[feature]['std']
                z_score = abs((value - mean) / std)
                
                if z_score > 5:  # More than 5 standard deviations
                    issues.append(f"{feature} value {value} is suspicious")
        
        # Check label consistency
        if self.is_label_inconsistent(data):
            issues.append("Label inconsistent with features")
        
        return len(issues) == 0, issues
    
    def is_label_inconsistent(self, data):
        """Check if label matches expected pattern"""
        # Use rule-based checks
        if data['cpu'] > 95 and data['label'] == 'normal':
            return True  # Suspicious
        
        return False

# Usage
validator = DataValidator()

for data_point in training_data:
    valid, issues = validator.validate_data_point(data_point)
    
    if not valid:
        alert_security_team(f"Suspicious data: {issues}")
        continue  # Skip suspicious data
    
    # Safe to use for training
    train_model(data_point)
```

---

### 2. Model Evasion Attacks

Attackers craft inputs to evade detection:

```python
# Attacker knows model thresholds
# Normal: CPU < 80
# Anomaly: CPU >= 80

# Attack: Keep CPU at 79% while degrading service
malicious_behavior = {
    'cpu': 79,  # Just under threshold
    'memory': 95,  # High but model doesn't weight heavily
    'latency': 5000  # Very high but masked
}

# Model predicts: normal (missed attack!)
```

**Defense - Multi-Feature Analysis**:

```python
class RobustAnomalyDetector:
    def __init__(self):
        self.model = load_model()
        self.rules = self.load_safety_rules()
    
    def predict(self, features):
        """Use model + rule-based safety checks"""
        
        # ML prediction
        ml_prediction = self.model.predict([features])[0]
        
        # Rule-based checks
        rule_alerts = []
        
        # Check for suspicious combinations
        if features['cpu'] > 75 and features['memory'] > 90:
            rule_alerts.append("High CPU + Memory")
        
        if features['latency'] > 3000:
            rule_alerts.append("Extreme latency")
        
        # Check for evasion patterns
        if self.is_evasion_attempt(features):
            rule_alerts.append("Possible evasion detected")
        
        # Combine ML and rules
        is_anomaly = (
            ml_prediction == -1 or 
            len(rule_alerts) >= 2  # Multiple rule violations
        )
        
        return {
            'is_anomaly': is_anomaly,
            'ml_prediction': ml_prediction,
            'rule_alerts': rule_alerts
        }
    
    def is_evasion_attempt(self, features):
        """Detect evasion patterns"""
        # Values just under thresholds are suspicious
        near_threshold = sum(
            1 for value, threshold in [
                (features['cpu'], 80),
                (features['memory'], 90),
                (features['disk'], 85)
            ]
            if abs(value - threshold) < 5  # Within 5% of threshold
        )
        
        return near_threshold >= 2

# Usage
detector = RobustAnomalyDetector()
result = detector.predict(suspicious_metrics)

if result['is_anomaly']:
    alert(f"Anomaly detected: {result['rule_alerts']}")
```

---

### 3. Model Extraction Attacks

Attackers query the model to steal it:

```python
# Attacker makes many queries to reverse-engineer model

for i in range(10000):
    test_input = generate_test_input()
    prediction = aiops_api.predict(test_input)
    
    # Collect input-output pairs
    training_data.append((test_input, prediction))

# Train copy of model
stolen_model = train_model(training_data)
```

**Defense - Rate Limiting & Query Monitoring**:

```python
from collections import defaultdict
import time

class APIProtection:
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.rate_limit = 100  # requests per hour
        self.suspicious_threshold = 50  # Similar queries
    
    def check_rate_limit(self, api_key):
        """Enforce rate limits"""
        now = time.time()
        hour_ago = now - 3600
        
        # Clean old requests
        self.request_counts[api_key] = [
            req_time for req_time in self.request_counts[api_key]
            if req_time > hour_ago
        ]
        
        # Check limit
        if len(self.request_counts[api_key]) >= self.rate_limit:
            return False, "Rate limit exceeded"
        
        # Record request
        self.request_counts[api_key].append(now)
        return True, "OK"
    
    def detect_extraction_attempt(self, api_key, features):
        """Detect model extraction attempts"""
        recent_queries = self.get_recent_queries(api_key, hours=1)
        
        # Check for systematic probing
        if len(recent_queries) > self.suspicious_threshold:
            # Check if queries are too similar (grid search pattern)
            similarity = calculate_query_similarity(recent_queries)
            
            if similarity > 0.8:  # Highly similar queries
                alert_security(f"Possible extraction attempt: {api_key}")
                return True
        
        return False

protection = APIProtection()

@app.post("/predict")
def predict(api_key: str, features: dict):
    # Check rate limit
    allowed, message = protection.check_rate_limit(api_key)
    if not allowed:
        raise HTTPException(status_code=429, detail=message)
    
    # Check for extraction attempt
    if protection.detect_extraction_attempt(api_key, features):
        raise HTTPException(status_code=403, detail="Suspicious activity")
    
    # Make prediction
    prediction = model.predict([features])
    return {'prediction': prediction}
```

---

## Data Privacy

### 1. Sensitive Data in Logs

Logs often contain sensitive information:

```python
# Bad: Sensitive data in logs
logger.info(f"User {user_id} payment {credit_card} failed")

# Bad: PII in metrics
metrics.send({
    'user_email': 'john@example.com',
    'order_value': 99.99
})
```

**Solution - Data Scrubbing**:

```python
import re

class DataScrubber:
    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'api_key': r'(api[_-]?key|token)[\s:=]+["\']?([a-zA-Z0-9_\-]+)["\']?'
        }
    
    def scrub_log_message(self, message):
        """Remove sensitive data from log message"""
        scrubbed = message
        
        for data_type, pattern in self.patterns.items():
            scrubbed = re.sub(
                pattern,
                f'[{data_type.upper()}_REDACTED]',
                scrubbed
            )
        
        return scrubbed
    
    def scrub_dict(self, data, sensitive_keys):
        """Remove sensitive keys from dict"""
        scrubbed = data.copy()
        
        for key in sensitive_keys:
            if key in scrubbed:
                scrubbed[key] = '[REDACTED]'
        
        return scrubbed

# Usage
scrubber = DataScrubber()

# Scrub logs before sending to AIOps
original_log = "User john@example.com payment 4532-1234-5678-9010 failed"
scrubbed_log = scrubber.scrub_log_message(original_log)
# → "User [EMAIL_REDACTED] payment [CREDIT_CARD_REDACTED] failed"

logger.info(scrubbed_log)

# Scrub metrics
original_metrics = {
    'user_email': 'john@example.com',
    'order_value': 99.99,
    'status': 'failed'
}

scrubbed_metrics = scrubber.scrub_dict(
    original_metrics,
    sensitive_keys=['user_email']
)
# → {'user_email': '[REDACTED]', 'order_value': 99.99, 'status': 'failed'}
```

---

### 2. Differential Privacy

Add noise to protect individual data points:

```python
import numpy as np

class DifferentialPrivacy:
    def __init__(self, epsilon=1.0):
        self.epsilon = epsilon  # Privacy budget
    
    def add_laplace_noise(self, value, sensitivity):
        """Add Laplace noise for differential privacy"""
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return value + noise
    
    def private_count(self, data, condition):
        """Count with differential privacy"""
        true_count = sum(1 for item in data if condition(item))
        
        # Sensitivity = 1 (one record changes count by at most 1)
        private_count = self.add_laplace_noise(true_count, sensitivity=1)
        
        return max(0, int(private_count))  # Ensure non-negative
    
    def private_mean(self, values, value_range):
        """Calculate mean with differential privacy"""
        true_mean = np.mean(values)
        
        # Sensitivity = (max - min) / n
        sensitivity = value_range / len(values)
        private_mean = self.add_laplace_noise(true_mean, sensitivity)
        
        return private_mean

# Usage
dp = DifferentialPrivacy(epsilon=1.0)

# Count anomalies privately
anomaly_count = dp.private_count(
    incidents,
    condition=lambda x: x['severity'] == 'high'
)

# Calculate average CPU privately
avg_cpu = dp.private_mean(
    cpu_values,
    value_range=100  # CPU: 0-100%
)

print(f"Anomalies (private): {anomaly_count}")
print(f"Avg CPU (private): {avg_cpu:.2f}%")
```

---

### 3. Data Encryption

Encrypt sensitive data at rest and in transit:

```python
from cryptography.fernet import Fernet
import os

class SecureDataStore:
    def __init__(self):
        # Load encryption key from secure location
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            print(f"Generated new key: {key.decode()}")
        else:
            key = key.encode()
        
        self.cipher = Fernet(key)
    
    def encrypt_data(self, data):
        """Encrypt data before storing"""
        json_data = json.dumps(data)
        encrypted = self.cipher.encrypt(json_data.encode())
        return encrypted
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data after retrieving"""
        decrypted = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted.decode())
    
    def store_securely(self, key, data):
        """Store data encrypted"""
        encrypted = self.encrypt_data(data)
        redis_client.set(key, encrypted)
    
    def retrieve_securely(self, key):
        """Retrieve and decrypt data"""
        encrypted = redis_client.get(key)
        if encrypted:
            return self.decrypt_data(encrypted)
        return None

# Usage
secure_store = SecureDataStore()

# Store sensitive metrics encrypted
sensitive_metrics = {
    'customer_id': 'CUST-12345',
    'revenue': 150000,
    'location': 'EU'
}

secure_store.store_securely('metrics:sensitive', sensitive_metrics)

# Retrieve and decrypt
decrypted = secure_store.retrieve_securely('metrics:sensitive')
```

---

## Compliance and Governance

### 1. GDPR Compliance

Right to be forgotten, data portability:

```python
class GDPRCompliantAIOps:
    def __init__(self):
        self.data_store = get_data_store()
        self.model_store = get_model_store()
    
    def delete_user_data(self, user_id):
        """Delete all data related to user (Right to be forgotten)"""
        # Delete from operational data
        self.data_store.delete_where(user_id=user_id)
        
        # Delete from training data
        self.model_store.remove_training_samples(user_id=user_id)
        
        # Flag models for retraining (trained on deleted data)
        affected_models = self.model_store.get_models_trained_with_user(user_id)
        for model in affected_models:
            model.mark_for_retraining()
        
        # Log deletion for audit
        audit_log.record({
            'action': 'user_data_deleted',
            'user_id': user_id,
            'timestamp': datetime.now(),
            'affected_models': [m.id for m in affected_models]
        })
    
    def export_user_data(self, user_id):
        """Export all data related to user (Data portability)"""
        # Collect all data
        user_data = {
            'metrics': self.data_store.get_user_metrics(user_id),
            'incidents': self.data_store.get_user_incidents(user_id),
            'alerts': self.data_store.get_user_alerts(user_id),
            'predictions': self.data_store.get_user_predictions(user_id)
        }
        
        # Return in standard format
        return {
            'user_id': user_id,
            'export_date': datetime.now().isoformat(),
            'data': user_data
        }
    
    def get_data_retention_policy(self):
        """Define data retention periods"""
        return {
            'metrics': '90 days',
            'logs': '30 days',
            'incidents': '1 year',
            'training_data': '2 years',
            'models': '1 year after replacement'
        }
    
    def enforce_retention_policy(self):
        """Delete data older than retention period"""
        policy = self.get_data_retention_policy()
        
        for data_type, retention_period in policy.items():
            cutoff_date = self.calculate_cutoff_date(retention_period)
            deleted = self.data_store.delete_older_than(data_type, cutoff_date)
            
            audit_log.record({
                'action': 'data_retention_enforcement',
                'data_type': data_type,
                'deleted_count': deleted,
                'cutoff_date': cutoff_date
            })
```

---

### 2. Audit Logging

Track all AIOps operations:

```python
class AuditLogger:
    def __init__(self):
        self.log_store = get_secure_log_store()
    
    def log_prediction(self, user, input_data, prediction, model_version):
        """Log model predictions for audit"""
        self.log_store.write({
            'event_type': 'prediction',
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'input_hash': hash(str(input_data)),  # Don't log raw data
            'prediction': prediction,
            'model_version': model_version,
            'confidence': prediction.get('confidence')
        })
    
    def log_model_update(self, model_name, old_version, new_version, reason):
        """Log model updates"""
        self.log_store.write({
            'event_type': 'model_update',
            'timestamp': datetime.now().isoformat(),
            'model_name': model_name,
            'old_version': old_version,
            'new_version': new_version,
            'reason': reason,
            'approved_by': get_current_user()
        })
    
    def log_data_access(self, user, data_type, query):
        """Log data access for compliance"""
        self.log_store.write({
            'event_type': 'data_access',
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'data_type': data_type,
            'query_hash': hash(str(query))
        })
    
    def generate_audit_report(self, start_date, end_date):
        """Generate audit report for compliance"""
        events = self.log_store.query(
            start_time=start_date,
            end_time=end_date
        )
        
        report = {
            'period': f"{start_date} to {end_date}",
            'total_predictions': len([e for e in events if e['event_type'] == 'prediction']),
            'model_updates': len([e for e in events if e['event_type'] == 'model_update']),
            'data_accesses': len([e for e in events if e['event_type'] == 'data_access']),
            'users': list(set(e['user'] for e in events if 'user' in e))
        }
        
        return report

# Usage
audit = AuditLogger()

# Log every prediction
prediction = model.predict(features)
audit.log_prediction(
    user='api_user_123',
    input_data=features,
    prediction=prediction,
    model_version='v2.1.0'
)

# Log model updates
audit.log_model_update(
    model_name='AnomalyDetector',
    old_version='v2.0.0',
    new_version='v2.1.0',
    reason='Improved accuracy from 95% to 97%'
)

# Generate monthly audit report
report = audit.generate_audit_report(
    start_date='2024-01-01',
    end_date='2024-01-31'
)
```

---

## Access Control

### 1. Role-Based Access Control (RBAC)

```python
from enum import Enum
from functools import wraps

class Role(Enum):
    VIEWER = 1
    ANALYST = 2
    ENGINEER = 3
    ADMIN = 4

class Permission(Enum):
    VIEW_METRICS = 'view_metrics'
    VIEW_LOGS = 'view_logs'
    TRIGGER_ANALYSIS = 'trigger_analysis'
    UPDATE_MODEL = 'update_model'
    MANAGE_USERS = 'manage_users'

# Define role permissions
ROLE_PERMISSIONS = {
    Role.VIEWER: [Permission.VIEW_METRICS],
    Role.ANALYST: [Permission.VIEW_METRICS, Permission.VIEW_LOGS, Permission.TRIGGER_ANALYSIS],
    Role.ENGINEER: [Permission.VIEW_METRICS, Permission.VIEW_LOGS, Permission.TRIGGER_ANALYSIS, Permission.UPDATE_MODEL],
    Role.ADMIN: [perm for perm in Permission]  # All permissions
}

class RBAC:
    def __init__(self):
        self.user_roles = {}
    
    def assign_role(self, user, role):
        """Assign role to user"""
        self.user_roles[user] = role
    
    def has_permission(self, user, permission):
        """Check if user has permission"""
        role = self.user_roles.get(user)
        if not role:
            return False
        
        return permission in ROLE_PERMISSIONS[role]
    
    def require_permission(self, permission):
        """Decorator to enforce permission"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user = get_current_user()
                
                if not self.has_permission(user, permission):
                    raise PermissionError(
                        f"User {user} lacks permission: {permission.value}"
                    )
                
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Usage
rbac = RBAC()

# Assign roles
rbac.assign_role('alice', Role.ADMIN)
rbac.assign_role('bob', Role.ANALYST)
rbac.assign_role('charlie', Role.VIEWER)

# Protect functions
@rbac.require_permission(Permission.UPDATE_MODEL)
def update_model(model_name, new_version):
    """Only engineers and admins can update models"""
    deploy_model(model_name, new_version)

@rbac.require_permission(Permission.VIEW_LOGS)
def view_logs(service, start_time, end_time):
    """Analysts and above can view logs"""
    return fetch_logs(service, start_time, end_time)

# Alice (admin) can update models
update_model('AnomalyDetector', 'v2.0')  # ✓ Success

# Charlie (viewer) cannot update models
# update_model('AnomalyDetector', 'v2.0')  # ✗ PermissionError
```

---

### 2. API Authentication

```python
import jwt
from datetime import datetime, timedelta

class TokenAuth:
    def __init__(self, secret_key):
        self.secret_key = secret_key
    
    def generate_token(self, user_id, role, expires_in_hours=24):
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token
    
    def verify_token(self, token):
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

# FastAPI example
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()
security = HTTPBearer()
auth = TokenAuth(secret_key='your-secret-key')

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user from token"""
    token = credentials.credentials
    
    try:
        payload = auth.verify_token(token)
        return payload
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/predict")
def predict(features: dict, current_user = Depends(get_current_user)):
    """Protected endpoint"""
    # Only authenticated users can make predictions
    prediction = model.predict([features])
    
    # Log for audit
    audit_log.log_prediction(
        user=current_user['user_id'],
        input_data=features,
        prediction=prediction
    )
    
    return {'prediction': prediction}
```

---

## Security Best Practices

### 1. Secure Configuration Management

```python
import os
from typing import Dict

class SecureConfig:
    """Load configuration from environment variables"""
    
    @staticmethod
    def get_database_url() -> str:
        """Get database URL from environment"""
        url = os.environ.get('DATABASE_URL')
        if not url:
            raise ConfigurationError("DATABASE_URL not set")
        return url
    
    @staticmethod
    def get_encryption_key() -> bytes:
        """Get encryption key from environment"""
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            raise ConfigurationError("ENCRYPTION_KEY not set")
        return key.encode()
    
    @staticmethod
    def get_api_rate_limits() -> Dict[str, int]:
        """Get rate limits from environment"""
        return {
            'requests_per_hour': int(os.environ.get('RATE_LIMIT_HOUR', '1000')),
            'requests_per_minute': int(os.environ.get('RATE_LIMIT_MINUTE', '100'))
        }

# Usage with docker
"""
# docker-compose.yml
services:
  aiops:
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - RATE_LIMIT_HOUR=1000
"""

# Load configuration securely
config = SecureConfig()
db_url = config.get_database_url()  # From environment, not hardcoded
```

---

### 2. Input Validation

```python
from pydantic import BaseModel, validator, Field

class PredictionRequest(BaseModel):
    """Validated prediction request"""
    
    service_name: str = Field(..., min_length=1, max_length=100)
    cpu_usage: float = Field(..., ge=0, le=100)
    memory_usage: float = Field(..., ge=0, le=100)
    latency_ms: float = Field(..., ge=0)
    
    @validator('service_name')
    def validate_service_name(cls, v):
        """Ensure service name is alphanumeric"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Service name must be alphanumeric')
        return v
    
    @validator('latency_ms')
    def validate_latency(cls, v):
        """Ensure latency is reasonable"""
        if v > 300000:  # 5 minutes
            raise ValueError('Latency too high (> 5 minutes)')
        return v

@app.post("/predict")
def predict(request: PredictionRequest):
    """Input is automatically validated by Pydantic"""
    features = [
        request.cpu_usage,
        request.memory_usage,
        request.latency_ms
    ]
    
    prediction = model.predict([features])
    return {'prediction': prediction}
```

---

## Summary

Security and privacy in AIOps require:

1. **Protect Models**: Validate training data, detect evasion
2. **Protect Data**: Scrub PII, encrypt sensitive data
3. **Compliance**: GDPR, data retention, audit logging
4. **Access Control**: RBAC, API authentication
5. **Best Practices**: Secure config, input validation, rate limiting

**Next**: [Real-World AIOps Project →](20-real-world-aiops-project.md)

