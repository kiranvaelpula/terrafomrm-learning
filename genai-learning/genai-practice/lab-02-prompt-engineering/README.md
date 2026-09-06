# Lab 02: Prompt Engineering — Log Analyzer

## 🎯 Objective
Build a log analyzer that extracts structured data from messy logs using prompt engineering techniques: role prompting, structured output, and few-shot examples.

## 📋 Prerequisites
```bash
pip install openai python-dotenv
export OPENAI_API_KEY=sk-your-key
```

## 🧪 Steps

### Step 1: Naive prompt (see the problem)
Ask the model to "analyze these logs" with no structure. Notice the output is inconsistent — sometimes prose, sometimes bullets, hard to parse.

### Step 2: Add role + structured output
Assign a role ("SRE") and demand JSON output with an exact schema. Now the output is consistent and parseable.

### Step 3: Add few-shot examples
Provide 1-2 examples of input→output to lock in the exact format you want.

### Step 4: Parse and use the output
Parse the JSON and act on it (e.g., filter by severity).

## ✅ Expected Output
```json
{
  "root_cause": "Database connection pool exhausted",
  "severity": "high",
  "affected_service": "payment-svc",
  "remediation_steps": ["Increase connection pool size", "Scale service replicas"]
}
```

## 🏋️ Exercises
1. Add a "confidence" field (0-1) to the output
2. Process a batch of log files and produce a summary report
3. Add a guardrail: if logs contain no errors, return `{"status": "healthy"}`
4. Compare `temperature=0` vs `temperature=0.7` — which is better for extraction?

## 🔑 Key Concepts Practiced
- Role/persona prompting
- Structured output (JSON schema)
- Few-shot prompting
- Temperature 0 for deterministic extraction
- Parsing LLM output safely
