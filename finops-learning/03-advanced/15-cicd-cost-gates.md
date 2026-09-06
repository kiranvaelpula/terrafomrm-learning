# CI/CD Cost Gates

## Overview

Cost gates estimate the cost impact of infrastructure changes inside the CI/CD pipeline — before deployment — so engineers see the price before merging.

---

## 📖 Understanding CI/CD Cost Gates (Intuition First)

A CI/CD cost gate is like the price tag that shows up *before* you click "buy," rather than the credit card statement that arrives weeks later. Today, most teams discover a costly infrastructure change only after it's been running and billing for a month. A cost gate moves that discovery all the way to the left — into the pull request — so an engineer sees "this change adds $4,200/month" while they're still writing the code and can decide whether it's worth it.

This idea is the FinOps version of a principle DevOps already loves: **shift left**. Just as we catch bugs and security issues earlier in the pipeline because they're cheaper to fix there, cost gates catch expensive infrastructure decisions at the cheapest possible moment — before deployment. The later you find a cost problem, the more it has already cost you and the harder it is to unwind.

The mechanism is straightforward. When an engineer changes infrastructure-as-code (like Terraform), a tool such as Infracost parses the diff and estimates the monthly cost impact, then posts it right in the pull request. The "gate" part means the pipeline can enforce a policy: warn on any increase, require approval above a threshold, or outright fail the build if a change would blow past a budget. It's a checkpoint the code must pass, just like tests or linting.

The deeper value is **cultural, not just financial**. When engineers see the cost of their choices in the same place they see their code, cost becomes a normal engineering consideration — like performance or security — instead of finance's problem after the fact. A well-placed cost comment on a PR quietly teaches the whole team that a bigger instance or an extra NAT gateway isn't free, changing behavior without anyone lecturing.

The art is in **tuning the gate so it helps rather than annoys**. Too strict and it blocks legitimate work and breeds resentment; too loose and it's ignored. The best gates are informational by default (always show the cost), enforcing only above meaningful thresholds, and framed as guidance — because the goal is cost-aware engineers making good decisions, not a bureaucratic roadblock that slows everyone down.

---

## How It Works (Infracost)

```
1. Engineer changes Terraform (adds an RDS instance)
2. Opens a pull request
3. CI pipeline runs Infracost on the Terraform diff
4. Infracost posts a comment: "This change adds $312/month"
5. Reviewer sees cost alongside code, decides if it's justified
6. Optional: gate FAILS the build if increase > threshold
```

## Example: GitHub Actions Cost Gate

```yaml
# .github/workflows/cost-gate.yml
name: Infracost
on: [pull_request]

jobs:
  cost-estimate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Infracost
        uses: infracost/actions/setup@v3
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}

      - name: Generate cost estimate for the base branch
        run: |
          infracost breakdown --path=. \
            --format=json --out-file=/tmp/base.json

      - name: Post cost diff comment on the PR
        run: |
          infracost diff --path=. \
            --compare-to=/tmp/base.json \
            --format=json --out-file=/tmp/diff.json
          infracost comment github --path=/tmp/diff.json \
            --repo=$GITHUB_REPOSITORY \
            --pull-request=${{ github.event.pull_request.number }} \
            --github-token=${{ secrets.GITHUB_TOKEN }}
```

## Enforcing a Policy (Fail the Build)

```yaml
      - name: Enforce cost threshold
        run: |
          # Extract the monthly cost increase from the diff
          INCREASE=$(jq '.diffTotalMonthlyCost | tonumber' /tmp/diff.json)
          echo "Monthly cost increase: \$$INCREASE"

          # Fail if increase exceeds $500/month without approval
          if (( $(echo "$INCREASE > 500" | bc -l) )); then
            echo "❌ Cost increase \$$INCREASE exceeds \$500 threshold."
            echo "Requires FinOps approval label to merge."
            exit 1
          fi
```

## Policy Design (Infracost Policies / OPA)

```
Gate levels (least to most strict):
1. INFORMATIONAL — always show cost, never block (start here)
2. WARN — flag increases above a threshold, allow merge
3. APPROVAL — require a reviewer/label above a threshold
4. BLOCK — fail the build above a hard limit

Recommended: informational by default, approval for large increases.
```

## What Cost Gates Catch

| Change | Typical cost surprise |
|--------|----------------------|
| Oversized instance type | m5.24xlarge instead of m5.large |
| Missing lifecycle policy | S3 data never transitions to cheaper tiers |
| Extra NAT Gateways | ~$32/mo each + data processing |
| Provisioned IOPS | io2 with high IOPS is very expensive |
| Multi-AZ everything | 2x cost when single-AZ would do for dev |

## Limitations

- Estimates are **projections**, not actual bills — usage-based costs (data transfer, requests) are approximate
- Doesn't catch runtime waste (idle resources) — that's monitoring's job
- Only as good as your IaC coverage — manually-created resources aren't seen

---

## 🎯 Interview Quick Points

- A **cost gate** shows the cost impact of an infrastructure change *before* deployment — in the pull request
- It's the FinOps application of **shift-left**: catch expensive decisions at the cheapest moment to fix them
- Typical tool: **Infracost** parses Terraform diffs and posts estimated monthly cost changes on the PR
- The "gate" enforces policy: **warn, require approval above a threshold, or fail the build**
- Estimates are **pre-deployment projections**, not actual billed cost — treat them as guidance
- The biggest value is **cultural** — cost becomes a normal engineering concern, like performance/security
- Tune thresholds carefully: **too strict breeds resentment, too loose gets ignored**
- Default to **informational** (always show cost); enforce only above meaningful dollar amounts
- Integrates into existing pipelines (GitHub Actions, GitLab CI, Jenkins) alongside tests and linting
- Pairs well with **tagging and budgets** so gates can reason about team/project limits
- Teaches engineers that bigger instances, extra NAT gateways, etc. **aren't free** — without lecturing
- Goal: **cost-aware engineers making good decisions**, not a bureaucratic roadblock that slows delivery
