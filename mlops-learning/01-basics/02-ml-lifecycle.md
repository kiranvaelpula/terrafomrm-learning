# ML Lifecycle Overview

## The Complete Machine Learning Lifecycle

The ML lifecycle is the end-to-end process of developing, deploying, and maintaining machine learning models in production.

## ML Lifecycle Stages

```
┌─────────────────────────────────────────────────────────────┐
│                    ML Lifecycle                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Problem Definition                                      │
│     ↓                                                       │
│  2. Data Collection & Exploration                          │
│     ↓                                                       │
│  3. Data Preparation & Feature Engineering                 │
│     ↓                                                       │
│  4. Model Training & Experimentation                       │
│     ↓                                                       │
│  5. Model Evaluation & Validation                          │
│     ↓                                                       │
│  6. Model Deployment                                       │
│     ↓                                                       │
│  7. Monitoring & Maintenance                               │
│     ↓                                                       │
│  8. Model Retraining ──────────────┐                      │
│                                     │                      │
│     └───────────────────────────────┘                      │
│           (Continuous Loop)                                │
└─────────────────────────────────────────────────────────────┘
```

## Stage 1: Problem Definition

**Objective**: Clearly define the business problem and ML approach

### Key Activities:
- Define business objectives
- Determine if ML is appropriate
- Define success metrics
- Identify data requirements
- Assess feasibility

### Example:
```yaml
Problem: Customer Churn Prediction

Business_Objective:
  goal: "Reduce customer churn by 20%"
  impact: "Save $2M annually"

ML_Approach:
  type: "Binary Classification"
  target: "Will customer churn in next 30 days?"
  
Success_Metrics:
  primary: "Precision (minimize false positives)"
  secondary: "Recall (catch most churners)"
  business: "Churn rate reduction"
  
Data_Requirements:
  - Customer demographics
  - Usage patterns (last 6 months)
  - Support tickets
  - Billing history
  - Product features used
  
Constraints:
  - Must predict 7 days in advance
  - Inference latency < 100ms
  - Model must be explainable (for customer retention team)
```

### Questions to Ask:
1. What business decision will this model support?
2. What's the cost of false positives vs false negatives?
3. How often does the model need to be updated?
4. What level of accuracy is "good enough"?
5. Are there regulatory/ethical considerations?

---

## Stage 2: Data Collection & Exploration

**Objective**: Gather and understand the data

### Key Activities:

**Data Collection**:
```python
# Example: Collecting data from multiple sources
import pandas as pd
from sqlalchemy import create_engine

# Database connection
engine = create_engine('postgresql://user:pass@localhost/db')

# Collect customer data
customers = pd.read_sql("""
    SELECT * FROM customers 
    WHERE created_date > '2023-01-01'
""", engine)

# Collect usage data
usage = pd.read_sql("""
    SELECT customer_id, feature, usage_count, last_used
    FROM usage_logs
    WHERE log_date > CURRENT_DATE - INTERVAL '6 months'
""", engine)

# API data
import requests
support_data = requests.get('https://api.support.com/tickets').json()

# Combine datasets
data = customers.merge(usage, on='customer_id')
```

**Exploratory Data Analysis (EDA)**:
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Basic statistics
print(data.describe())
print(data.info())

# Check missing values
print(data.isnull().sum())

# Distribution of target variable
sns.countplot(data['churned'])
plt.title('Churn Distribution')
plt.show()

# Feature correlations
correlation = data.corr()
sns.heatmap(correlation, annot=True)
plt.show()

# Analyze churn patterns
churned = data[data['churned'] == 1]
retained = data[data['churned'] == 0]

print("Average usage - Churned:", churned['usage_count'].mean())
print("Average usage - Retained:", retained['usage_count'].mean())
```

**Data Quality Checks**:
```python
def check_data_quality(df):
    """Validate data quality"""
    issues = []
    
    # Check for duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        issues.append(f"Found {duplicates} duplicate rows")
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.any():
        issues.append(f"Missing values:\n{missing[missing > 0]}")
    
    # Check for outliers
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df[col] < (Q1 - 1.5 * IQR)) | 
                   (df[col] > (Q3 + 1.5 * IQR))).sum()
        if outliers > 0:
            issues.append(f"{col}: {outliers} outliers")
    
    return issues
```

---

## Stage 3: Data Preparation & Feature Engineering

**Objective**: Transform raw data into model-ready features

### Data Cleaning:
```python
# Handle missing values
data['age'].fillna(data['age'].median(), inplace=True)
data['last_login'].fillna(method='ffill', inplace=True)

# Remove duplicates
data = data.drop_duplicates(subset=['customer_id'])

# Handle outliers
from scipy import stats
z_scores = stats.zscore(data['transaction_amount'])
data = data[(z_scores < 3) & (z_scores > -3)]

# Fix data types
data['signup_date'] = pd.to_datetime(data['signup_date'])
data['customer_id'] = data['customer_id'].astype(str)
```

### Feature Engineering:
```python
# Create time-based features
data['account_age_days'] = (pd.Timestamp.now() - data['signup_date']).dt.days
data['days_since_last_login'] = (pd.Timestamp.now() - data['last_login']).dt.days

# Aggregation features
data['avg_monthly_usage'] = data['total_usage'] / data['account_age_days'] * 30
data['support_ticket_rate'] = data['ticket_count'] / data['account_age_days']

# Categorical encoding
data = pd.get_dummies(data, columns=['subscription_type', 'country'])

# Interaction features
data['usage_x_age'] = data['avg_monthly_usage'] * data['account_age_days']

# Domain-specific features
data['is_power_user'] = (data['avg_monthly_usage'] > data['avg_monthly_usage'].quantile(0.75)).astype(int)
data['at_risk'] = ((data['days_since_last_login'] > 30) & 
                   (data['support_ticket_rate'] > 0.1)).astype(int)
```

### Feature Selection:
```python
from sklearn.feature_selection import SelectKBest, mutual_info_classif

# Select top features
selector = SelectKBest(mutual_info_classif, k=20)
X_selected = selector.fit_transform(X, y)

# Get feature scores
feature_scores = pd.DataFrame({
    'feature': X.columns,
    'score': selector.scores_
}).sort_values('score', ascending=False)

print("Top 10 features:")
print(feature_scores.head(10))
```

---

## Stage 4: Model Training & Experimentation

**Objective**: Train and optimize ML models

### Train Multiple Models:
```python
import mlflow
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

mlflow.set_experiment("churn-prediction")

models = {
    'logistic_regression': LogisticRegression(),
    'random_forest': RandomForestClassifier(n_estimators=100),
    'gradient_boosting': GradientBoostingClassifier(n_estimators=100)
}

for name, model in models.items():
    with mlflow.start_run(run_name=name):
        # Train
        model.fit(X_train, y_train)
        
        # Evaluate
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        # Log
        mlflow.log_param("model_type", name)
        mlflow.log_metric("train_accuracy", train_score)
        mlflow.log_metric("test_accuracy", test_score)
        mlflow.sklearn.log_model(model, "model")
        
        print(f"{name}: Train={train_score:.3f}, Test={test_score:.3f}")
```

### Hyperparameter Tuning:
```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15],
    'min_samples_split': [2, 5, 10]
}

grid_search = GridSearchCV(
    RandomForestClassifier(),
    param_grid,
    cv=5,
    scoring='f1',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

print("Best parameters:", grid_search.best_params_)
print("Best F1 score:", grid_search.best_score_)

# Log best model
with mlflow.start_run(run_name="best_rf_model"):
    mlflow.log_params(grid_search.best_params_)
    mlflow.log_metric("cv_f1_score", grid_search.best_score_)
    mlflow.sklearn.log_model(grid_search.best_estimator_, "model")
```

---

## Stage 5: Model Evaluation & Validation

**Objective**: Thoroughly evaluate model performance

### Comprehensive Evaluation:
```python
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix,
                             classification_report)

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

# Calculate metrics
metrics = {
    'accuracy': accuracy_score(y_test, predictions),
    'precision': precision_score(y_test, predictions),
    'recall': recall_score(y_test, predictions),
    'f1': f1_score(y_test, predictions),
    'roc_auc': roc_auc_score(y_test, probabilities)
}

print("Model Performance:")
for metric, value in metrics.items():
    print(f"  {metric}: {value:.4f}")

# Confusion Matrix
cm = confusion_matrix(y_test, predictions)
sns.heatmap(cm, annot=True, fmt='d')
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()

# Classification Report
print(classification_report(y_test, predictions))
```

### Business Impact Analysis:
```python
def calculate_business_impact(predictions, actuals, costs):
    """Calculate financial impact of model"""
    TP = ((predictions == 1) & (actuals == 1)).sum()  # Correct churn predictions
    FP = ((predictions == 1) & (actuals == 0)).sum()  # False alarms
    FN = ((predictions == 0) & (actuals == 1)).sum()  # Missed churns
    TN = ((predictions == 0) & (actuals == 0)).sum()  # Correct retentions
    
    # Calculate costs/benefits
    retention_cost = costs['retention_offer']  # $50 per offer
    churn_cost = costs['lost_customer']  # $500 per churned customer
    
    # Savings from correctly predicting churners
    savings = TP * (churn_cost - retention_cost)
    
    # Cost of false positives (unnecessary retention offers)
    fp_cost = FP * retention_cost
    
    # Cost of false negatives (missed churners)
    fn_cost = FN * churn_cost
    
    net_benefit = savings - fp_cost - fn_cost
    
    return {
        'total_savings': savings,
        'false_positive_cost': fp_cost,
        'false_negative_cost': fn_cost,
        'net_benefit': net_benefit,
        'roi': (net_benefit / (TP + FP) * retention_cost) * 100
    }

costs = {'retention_offer': 50, 'lost_customer': 500}
impact = calculate_business_impact(predictions, y_test, costs)
print(f"Net Benefit: ${impact['net_benefit']:,.2f}")
print(f"ROI: {impact['roi']:.1f}%")
```

---

## Stage 6: Model Deployment

**Objective**: Deploy model to production

### Deployment Options:

**1. REST API with Flask**:
```python
from flask import Flask, request, jsonify
import mlflow.sklearn

app = Flask(__name__)

# Load model
model = mlflow.sklearn.load_model("models:/churn-predictor/production")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    features = pd.DataFrame([data['features']])
    
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]
    
    return jsonify({
        'will_churn': bool(prediction),
        'churn_probability': float(probability),
        'risk_level': 'HIGH' if probability > 0.7 else 'MEDIUM' if probability > 0.4 else 'LOW'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**2. Batch Predictions**:
```python
def batch_predict(input_file, output_file):
    """Run predictions on batch of customers"""
    # Load data
    customers = pd.read_csv(input_file)
    
    # Load model
    model = mlflow.sklearn.load_model("models:/churn-predictor/production")
    
    # Prepare features
    features = prepare_features(customers)
    
    # Predict
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)[:, 1]
    
    # Add results
    customers['churn_prediction'] = predictions
    customers['churn_probability'] = probabilities
    customers['prediction_date'] = pd.Timestamp.now()
    
    # Save
    customers.to_csv(output_file, index=False)
    
    print(f"Processed {len(customers)} customers")
    print(f"Predicted {predictions.sum()} will churn")

# Run daily
batch_predict('data/daily_customers.csv', 'predictions/churn_predictions.csv')
```

---

## Stage 7: Monitoring & Maintenance

**Objective**: Track model performance in production

### Performance Monitoring:
```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset

# Monitor predictions
def monitor_model_performance():
    # Load reference data (training data)
    reference = pd.read_csv('data/reference_data.csv')
    
    # Load current production data
    current = pd.read_csv('predictions/recent_predictions.csv')
    
    # Create drift report
    report = Report(metrics=[
        DataDriftPreset(),
        DataQualityPreset()
    ])
    
    report.run(reference_data=reference, current_data=current)
    report.save_html('reports/drift_report.html')
    
    # Check for drift
    if report.as_dict()['metrics'][0]['result']['dataset_drift']:
        send_alert("Data drift detected!")
        trigger_retraining()
```

### Logging Predictions:
```python
def log_prediction(customer_id, features, prediction, probability):
    """Log all predictions for monitoring"""
    log_entry = {
        'timestamp': datetime.utcnow(),
        'customer_id': customer_id,
        'prediction': prediction,
        'probability': probability,
        'features': features,
        'model_version': get_model_version()
    }
    
    # Store in database
    db.predictions.insert_one(log_entry)
    
    # Track metrics
    prediction_counter.inc()
    prediction_latency.observe(time_elapsed)
```

---

## Stage 8: Model Retraining

**Objective**: Keep model current with new data

### Automated Retraining:
```python
def should_retrain():
    """Decide if model needs retraining"""
    # Check performance degradation
    recent_accuracy = get_recent_accuracy()
    baseline_accuracy = 0.85
    
    if recent_accuracy < baseline_accuracy - 0.05:
        return True, "Performance degraded"
    
    # Check data drift
    if detect_data_drift():
        return True, "Data drift detected"
    
    # Check time since last training
    days_since_training = (datetime.now() - last_training_date).days
    if days_since_training > 30:
        return True, "Scheduled retraining"
    
    return False, "Model still performing well"

# Retraining pipeline
def retrain_model():
    """Automated retraining pipeline"""
    print("Starting retraining...")
    
    # 1. Collect new data
    new_data = collect_recent_data(days=30)
    
    # 2. Combine with historical data
    all_data = pd.concat([historical_data, new_data])
    
    # 3. Prepare features
    X, y = prepare_features(all_data)
    
    # 4. Train new model
    model = train_model(X, y)
    
    # 5. Validate
    if validate_model(model):
        # 6. Deploy
        deploy_model(model, stage='staging')
        run_ab_test()
    else:
        send_alert("New model failed validation")
```

## Next Steps

Continue to [Development Environment Setup](03-environment-setup.md) to configure your MLOps tools.

---

**Remember**: The ML lifecycle is iterative—expect to revisit earlier stages as you learn more about your problem and data.
