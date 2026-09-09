#!/usr/bin/env python3
"""
Lab 05: A simple, controlled chaos experiment.
Kills ONE pod and verifies the service maintains steady state (self-heals).
Run against a LOCAL/test cluster only.
"""

import subprocess
import time
import random


def run(cmd):
    """Run a kubectl command, return stdout."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def get_pods(label="app=nginx"):
    out = run(["kubectl", "get", "pods", "-l", label, "--no-headers",
               "-o", "custom-columns=NAME:.metadata.name,STATUS:.status.phase"])
    return [line.split() for line in out.splitlines() if line]


def ready_count(label="app=nginx"):
    pods = get_pods(label)
    return sum(1 for _, status in pods if status == "Running")


def steady_state(label="app=nginx", expected=3):
    """Our hypothesis: the service maintains `expected` running pods."""
    ready = ready_count(label)
    ok = ready >= expected - 1   # tolerate one down during recovery
    print(f"  Steady state: {ready}/{expected} pods running "
          f"{'✓' if ok else '✗'}")
    return ok


def run_experiment(label="app=nginx", expected=3):
    print("═══ Chaos Experiment: Pod Deletion ═══\n")

    # 1. Hypothesis
    print("Hypothesis: killing 1 pod → service stays available "
          "(Kubernetes reschedules it)\n")

    # 2. Establish steady state
    print("Step 1: Verify steady state BEFORE chaos")
    if not steady_state(label, expected):
        print("  System not healthy — aborting experiment.")
        return

    # 3. Inject failure (smallest blast radius: 1 pod)
    pods = get_pods(label)
    victim = random.choice(pods)[0]
    print(f"\nStep 2: CHAOS — deleting pod {victim}")
    run(["kubectl", "delete", "pod", victim])

    # 4. Observe recovery
    print("\nStep 3: Observe recovery")
    for t in range(0, 30, 3):
        ready = ready_count(label)
        print(f"  t+{t}s: {ready}/{expected} pods ready")
        if ready >= expected:
            print("\nHypothesis CONFIRMED: service self-healed ✓")
            return
        time.sleep(3)

    print("\nHypothesis NOT confirmed — investigate why recovery is slow ✗")


if __name__ == "__main__":
    print("⚠️  Run against a LOCAL/test cluster only.\n")
    run_experiment()
