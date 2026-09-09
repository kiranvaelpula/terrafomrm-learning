#!/usr/bin/env python3
"""
Lab 04: Reliability patterns — retry with backoff and circuit breaker.
Demonstrates how they protect against a flaky dependency.
"""

import time
import random


class FlakyService:
    """A dependency that fails intermittently and sometimes goes fully down."""
    def __init__(self):
        self.down = False

    def call(self):
        if self.down:
            raise ConnectionError("service is DOWN")
        if random.random() < 0.4:            # 40% transient failure
            raise ConnectionError("transient failure")
        return "OK"


# ── Pattern 1: Retry with exponential backoff + jitter ──
def retry_with_backoff(func, max_attempts=4, base_delay=1):
    for attempt in range(1, max_attempts + 1):
        try:
            result = func()
            print(f"  Attempt {attempt} succeeded")
            return result
        except Exception as e:
            if attempt == max_attempts:
                print(f"  Attempt {attempt} failed ({e}) — giving up")
                raise
            delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            print(f"  Attempt {attempt} failed ({e}), retrying in {delay:.1f}s...")
            time.sleep(delay)


# ── Pattern 2: Circuit breaker ──
class CircuitBreaker:
    def __init__(self, failure_threshold=5, cooldown=3):
        self.failures = 0
        self.threshold = failure_threshold
        self.cooldown = cooldown
        self.state = "CLOSED"
        self.opened_at = None

    def call(self, func):
        if self.state == "OPEN":
            if time.time() - self.opened_at > self.cooldown:
                self.state = "HALF-OPEN"
                print("  Circuit HALF-OPEN — trying a test call")
            else:
                raise Exception("Circuit OPEN — failing fast (system protected)")

        try:
            result = func()
            if self.state == "HALF-OPEN":
                print("  Test call succeeded → Circuit CLOSED (recovered)")
            self.failures = 0
            self.state = "CLOSED"
            return result
        except Exception:
            self.failures += 1
            if self.failures >= self.threshold:
                self.state = "OPEN"
                self.opened_at = time.time()
                print(f"  Failures: {self.failures} → Circuit OPEN (failing fast)")
            raise


if __name__ == "__main__":
    svc = FlakyService()

    print("─── Pattern 1: Retry with backoff ───")
    try:
        retry_with_backoff(svc.call)
    except Exception:
        print("  (all retries exhausted)")

    print("\n─── Pattern 2: Circuit breaker (service goes down) ───")
    svc.down = True                          # simulate full outage
    breaker = CircuitBreaker(failure_threshold=5, cooldown=3)
    for i in range(8):
        try:
            breaker.call(svc.call)
        except Exception as e:
            print(f"  Call {i+1}: {e}")
        time.sleep(0.5)
