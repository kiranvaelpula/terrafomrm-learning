# Lab 04: Reliability Patterns

## 🎯 Objective
Implement a circuit breaker and retry-with-backoff, then see how they prevent cascading failures against a flaky dependency.

## 📋 Prerequisites
```bash
python3 --version   # no external libs
```

## 🧪 Steps

### Step 1: Simulate a flaky dependency
Run `patterns.py`. It has a "service" that fails intermittently and sometimes goes fully down.

### Step 2: See failure WITHOUT protection
Watch naive calls hang/fail and hammer the broken service.

### Step 3: Add retry with backoff
See transient failures recover via retries with increasing delays + jitter.

### Step 4: Add a circuit breaker
See it trip OPEN after repeated failures (fail fast), then recover via HALF-OPEN.

## ✅ Expected Output
```
--- Retry with backoff ---
Attempt 1 failed, retrying in 1.3s...
Attempt 2 succeeded

--- Circuit breaker ---
Failures: 5 → Circuit OPEN (failing fast, protecting the system)
After cooldown → HALF-OPEN → test call succeeds → CLOSED
```

## 🏋️ Exercises
1. Add a timeout wrapper (fail if a call takes too long)
2. Add graceful degradation (return a cached/default value when circuit is OPEN)
3. Combine retry + circuit breaker + timeout into one resilient client
4. Add a bulkhead (separate resource pools per dependency)

## 🔑 Key Concepts Practiced
- Retry with exponential backoff + jitter
- Circuit breaker (CLOSED / OPEN / HALF-OPEN)
- Failing fast to prevent cascades
- Graceful degradation (in exercises)
