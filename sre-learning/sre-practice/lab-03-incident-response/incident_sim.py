#!/usr/bin/env python3
"""
Lab 03: Incident response simulation.
Models the incident lifecycle and generates a blameless post-mortem skeleton.
"""

from datetime import datetime, timedelta
from enum import Enum


class Severity(Enum):
    SEV1 = "Critical"
    SEV2 = "High"
    SEV3 = "Medium"
    SEV4 = "Low"


class Incident:
    def __init__(self, title, severity, commander):
        self.title = title
        self.severity = severity
        self.commander = commander
        self.started = datetime.utcnow()
        self.resolved_at = None
        self.timeline = []

    def log(self, who, action):
        t = datetime.utcnow()
        self.timeline.append((t, who, action))
        print(f"[{t:%H:%M:%S}] {who}: {action}")

    def mitigate(self, who, action):
        self.log(who, f"MITIGATION: {action}")

    def resolve(self, who):
        self.resolved_at = datetime.utcnow()
        mttr = int((self.resolved_at - self.started).total_seconds() // 60)
        self.log(who, f"RESOLVED (MTTR: {mttr} min)")
        return mttr

    def generate_postmortem(self):
        """Produce a blameless post-mortem skeleton pre-filled with the timeline."""
        mttr = "N/A"
        if self.resolved_at:
            mttr = f"{int((self.resolved_at - self.started).total_seconds() // 60)} min"

        print("\n" + "=" * 50)
        print("POST-MORTEM SKELETON (blameless)")
        print("=" * 50)
        print(f"# Post-Mortem: {self.title}\n")
        print(f"## Summary\n{self.severity.value} incident. Duration: {mttr}.\n")
        print("## Timeline (UTC)")
        for t, who, action in self.timeline:
            print(f"- {t:%H:%M:%S} — {action} ({who})")
        print("\n## Root Cause")
        print("(Use the 5 Whys — focus on the SYSTEM, not the person)\n")
        print("## What Went Well / What Went Wrong")
        print("- ...\n")
        print("## Action Items (owner + due date)")
        print("| Action | Owner | Due | Priority |")
        print("|--------|-------|-----|----------|")
        print("| ...    | ...   | ... | ...      |")


if __name__ == "__main__":
    # Simulate an incident
    inc = Incident("Payment API 5xx spike", Severity.SEV1, commander="alice")

    inc.log("monitoring", "Detected via error-rate alert")
    inc.log("alice", "Incident declared SEV1, IC assigned, team paged")
    inc.log("bob", "Investigating — recent deploy v2.3 suspected")
    inc.log("bob", "Confirmed: v2.3 introduced a connection leak")
    inc.mitigate("bob", "Rolled back deploy to v2.2")
    inc.log("carol", "Error rate back to normal, verifying")
    inc.resolve("alice")

    inc.generate_postmortem()
