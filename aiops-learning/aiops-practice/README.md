# AIOps Practice Labs

Hands-on exercises to build practical AIOps skills using AI/ML for IT operations.

## 🎯 Overview

This directory contains practical labs covering anomaly detection, log analysis, predictive analytics, and automated remediation.

## 📚 Lab Structure

### Lab 1: Anomaly Detection
**Duration**: 1 hour  
**Skills**: Time series analysis, outlier detection  
**Folder**: `lab-01-anomaly-detection/`

### Lab 2: Log Analysis & Pattern Recognition
**Duration**: 1.5 hours  
**Skills**: NLP, log parsing, pattern matching  
**Folder**: `lab-02-log-analysis/`

### Lab 3: Root Cause Analysis
**Duration**: 1.5 hours  
**Skills**: Correlation, graph analytics, RCA  
**Folder**: `lab-03-root-cause-analysis/`

### Lab 4: Predictive Analytics
**Duration**: 1.5 hours  
**Skills**: Time series forecasting, capacity planning  
**Folder**: `lab-04-predictive-analytics/`

### Lab 5: Alert Correlation
**Duration**: 1 hour  
**Skills**: Event correlation, alert deduplication  
**Folder**: `lab-05-alert-correlation/`

### Lab 6: Automated Remediation
**Duration**: 1.5 hours  
**Skills**: Runbook automation, self-healing  
**Folder**: `lab-06-automated-remediation/`

### Lab 7: Metrics Monitoring
**Duration**: 1 hour  
**Skills**: Prometheus, Grafana, custom metrics  
**Folder**: `lab-07-metrics-monitoring/`

### Lab 8: Complete AIOps Platform
**Duration**: 3 hours  
**Skills**: End-to-end AIOps implementation  
**Folder**: `lab-08-complete-platform/`

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Navigate to a lab
cd lab-01-anomaly-detection

# Read instructions
cat README.md

# Run exercises
python exercises.py

# Verify your work
python verify.py
```

## 📋 Prerequisites

- Python 3.8+
- Docker (for running sample services)
- Basic understanding of monitoring concepts
- Familiarity with logs and metrics

## 🛠️ Required Tools

Install all tools:

```bash
# Core ML/Data tools
pip install pandas numpy scikit-learn scipy

# Time series & forecasting
pip install prophet statsmodels

# Anomaly detection
pip install pyod adtk

# Log analysis
pip install elasticsearch python-logstash nltk

# Visualization
pip install matplotlib seaborn plotly

# Monitoring
pip install prometheus-client grafana-api

# Automation
pip install ansible-runner

# Additional utilities
pip install jupyter notebook pytest
```

## 📊 Sample Datasets

All labs use realistic operational data:

1. **Metrics Data** (`data/metrics/`)
   - CPU, Memory, Disk, Network time series
   - 30 days of 1-minute resolution data
   - Includes normal and anomalous behavior

2. **Log Data** (`data/logs/`)
   - Application logs (10M+ lines)
   - System logs
   - Error patterns and incidents

3. **Event Data** (`data/events/`)
   - Alerts from monitoring systems
   - Change events (deployments, configs)
   - Incident records

4. **Topology Data** (`data/topology/`)
   - Service dependency graphs
   - Infrastructure relationships

## 🏗️ Project Structure

```
aiops-practice/
├── data/
│   ├── metrics/              # Time series metrics
│   ├── logs/                 # Log files
│   ├── events/               # Alert events
│   └── topology/             # Service dependencies
├── notebooks/                # Jupyter notebooks
│   ├── anomaly-detection.ipynb
│   ├── log-analysis.ipynb
│   └── forecasting.ipynb
├── src/
│   ├── anomaly/              # Anomaly detection code
│   ├── logs/                 # Log analysis code
│   ├── prediction/           # Forecasting code
│   ├── correlation/          # Event correlation
│   └── automation/           # Remediation scripts
├── models/                   # Trained models
├── dashboards/               # Grafana dashboards
└── lab-XX-*/                 # Individual labs
```

## 🏆 Completion Checklist

Track your progress:

- [ ] Lab 1: Anomaly Detection
- [ ] Lab 2: Log Analysis & Pattern Recognition
- [ ] Lab 3: Root Cause Analysis
- [ ] Lab 4: Predictive Analytics
- [ ] Lab 5: Alert Correlation
- [ ] Lab 6: Automated Remediation
- [ ] Lab 7: Metrics Monitoring
- [ ] Lab 8: Complete AIOps Platform

## 🎓 Learning Path

**Beginner** (Start here):
1. Lab 1: Anomaly Detection
2. Lab 2: Log Analysis
3. Lab 7: Metrics Monitoring

**Intermediate**:
4. Lab 4: Predictive Analytics
5. Lab 5: Alert Correlation
6. Lab 3: Root Cause Analysis

**Advanced**:
7. Lab 6: Automated Remediation
8. Lab 8: Complete AIOps Platform

## 📈 Success Metrics

After completing these labs, you should be able to:

✅ Detect anomalies in time series metrics  
✅ Analyze logs for patterns and insights  
✅ Perform root cause analysis on incidents  
✅ Predict capacity and performance issues  
✅ Correlate related alerts  
✅ Implement automated remediation  
✅ Build end-to-end AIOps solutions  
✅ Reduce MTTR and MTTD significantly  

## 🎯 Real-World Scenarios

Each lab includes realistic scenarios:

### Scenario 1: E-commerce Platform
- 1000+ microservices
- Black Friday traffic spike
- Detect and predict performance issues

### Scenario 2: Financial Services
- High-availability requirements
- Compliance logging
- Incident response automation

### Scenario 3: SaaS Application
- Multi-tenant environment
- Cost optimization
- Proactive capacity planning

## 🔧 Docker Environment

Run sample services for practice:

```bash
# Start sample infrastructure
cd docker-environment
docker-compose up -d

# Services include:
# - Prometheus (metrics)
# - Grafana (visualization)
# - Elasticsearch (logs)
# - Sample web app (generates metrics/logs)
```

## 📊 Key Concepts Covered

### Anomaly Detection
- Statistical methods (Z-score, IQR)
- Machine learning (Isolation Forest, LSTM)
- Seasonality and trend analysis
- Multi-metric anomaly detection

### Log Analysis
- Log parsing and normalization
- Pattern recognition
- Error classification
- Semantic analysis with NLP

### Predictive Analytics
- Time series forecasting (ARIMA, Prophet)
- Capacity planning
- Failure prediction
- Resource optimization

### Alert Management
- Alert correlation
- Noise reduction
- Priority scoring
- Intelligent grouping

### Automation
- Runbook automation
- Self-healing systems
- Dynamic scaling
- Configuration management

## 🎓 Certification Prep

These labs help prepare for:
- **Datadog Certified: Operations Professional**
- **Splunk Core Certified Power User**
- **AWS Certified DevOps Engineer - Professional**
- **Google Cloud Professional Cloud Architect**

## 📖 Additional Resources

### Documentation
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [ELK Stack Guide](https://www.elastic.co/guide/)
- [Prophet Documentation](https://facebook.github.io/prophet/)

### Papers
- "AIOps: Real-World Challenges and Research Innovations" (ACM)
- "Anomaly Detection for Monitoring" (Google SRE)

### Tools
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Elasticsearch](https://www.elastic.co/)
- [Falco](https://falco.org/)

## 💡 Tips for Success

1. **Start Simple**: Begin with basic anomaly detection, then advance
2. **Use Real Data**: Practice with actual logs and metrics when possible
3. **Tune Algorithms**: One size doesn't fit all - adjust for your environment
4. **Validate Results**: Always verify AI findings before automating actions
5. **Iterate**: AIOps models improve over time with feedback

## 🤝 Contributing

Found an issue or want to add a lab? Submit a PR!

## 📝 License

These practice materials are for educational purposes.
