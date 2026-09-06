# Reinforcement Learning for Auto-Remediation

## Overview

This chapter covers using **Reinforcement Learning (RL)** to build auto-remediation systems that *learn* the best actions to resolve incidents over time, rather than following fixed rules.

## 📖 Understanding RL Auto-Remediation (Intuition First)

Most auto-remediation is rule-based: "if CPU > 90%, scale up." That works for known problems but is rigid — someone has to write every rule, and rules can't adapt to new situations.

Reinforcement Learning takes a different approach, and the best analogy is **training a dog**. You don't give a dog a rulebook. Instead, when it does something good, you give it a treat (reward); when it does something bad, no treat (or a correction). Over many repetitions, the dog learns which actions lead to rewards. It figures out the *policy* on its own.

RL auto-remediation works the same way. The system (the "agent") observes the state of your infrastructure, takes an action (scale, restart, reroute traffic), and gets a reward based on the outcome — did the incident resolve? did latency improve? did it avoid causing a new problem? Over time, it learns a *policy*: the best action to take in each situation, including situations no human explicitly programmed.

The power is **adaptation**. A rule-based system does exactly what it was told, forever. An RL system keeps learning — as your infrastructure changes, traffic patterns shift, and new failure modes appear, it adapts its strategy based on what actually works.

The catch is that RL needs to *explore* to learn, and exploration in production is dangerous (you can't have it randomly restarting production services to "see what happens"). So real-world RL remediation is trained in simulation or on historical data first, and deployed with strong guardrails.

---

## 🧠 Core RL Concepts

```
┌─────────────┐   action    ┌──────────────┐
│   Agent      │────────────▶│ Environment   │
│ (remediation │             │(your infra)   │
│  policy)     │◀────────────│               │
└─────────────┘  state +     └──────────────┘
                 reward
```

| Term | Meaning | AIOps example |
|------|---------|---------------|
| **Agent** | The decision-maker | The remediation controller |
| **Environment** | What the agent acts on | Your infrastructure |
| **State** | Current situation | CPU 95%, latency 800ms, 3 pods |
| **Action** | What the agent can do | Scale, restart, reroute, do nothing |
| **Reward** | Feedback signal | +1 if resolved, -1 if made worse |
| **Policy** | Learned strategy | State → best action mapping |

---

## 🎯 Reward Function Design (The Hard Part)

The reward function defines what "good" means — get it wrong and the agent learns the wrong behavior.

```python
def calculate_reward(state_before, action, state_after):
    """Reward the agent for resolving incidents efficiently and safely."""
    reward = 0

    # Reward resolving the problem
    if state_after['healthy'] and not state_before['healthy']:
        reward += 100

    # Reward improving key metrics
    latency_improvement = state_before['latency'] - state_after['latency']
    reward += latency_improvement * 0.1

    # PENALIZE causing new problems
    if state_after['error_rate'] > state_before['error_rate']:
        reward -= 50

    # PENALIZE expensive actions (don't over-scale)
    if action == 'scale_up':
        reward -= 5   # small cost for adding resources

    # PENALIZE unnecessary action when system was already healthy
    if state_before['healthy'] and action != 'do_nothing':
        reward -= 20

    return reward
```

Notice it rewards resolution AND penalizes side effects, cost, and needless action. A naive reward ("+1 if healthy") could teach the agent to over-provision wastefully.

---

## 🛠️ Simplified Q-Learning Example

```python
import numpy as np
import random

class RemediationAgent:
    """A simple Q-learning agent for auto-remediation (illustrative)."""

    def __init__(self, states, actions, lr=0.1, gamma=0.9, epsilon=0.1):
        self.actions = actions
        self.q_table = {s: {a: 0.0 for a in actions} for s in states}
        self.lr = lr          # learning rate
        self.gamma = gamma    # discount factor (value of future rewards)
        self.epsilon = epsilon  # exploration rate

    def choose_action(self, state):
        # Explore occasionally, otherwise exploit best known action
        if random.random() < self.epsilon:
            return random.choice(self.actions)     # explore
        return max(self.q_table[state], key=self.q_table[state].get)  # exploit

    def learn(self, state, action, reward, next_state):
        # Q-learning update rule
        old_value = self.q_table[state][action]
        next_max = max(self.q_table[next_state].values())
        new_value = old_value + self.lr * (reward + self.gamma * next_max - old_value)
        self.q_table[state][action] = new_value


# States and actions (simplified)
states = ["healthy", "high_cpu", "high_latency", "degraded"]
actions = ["do_nothing", "scale_up", "restart", "reroute"]

agent = RemediationAgent(states, actions)

# Training happens in SIMULATION or on historical data, never randomly in prod
```

---

## ⚠️ Production Guardrails (Non-Negotiable)

RL exploration in production is dangerous. Real deployments use:

```
1. Train offline first — in simulation or on historical incident data
2. Shadow mode — the agent SUGGESTS actions, humans approve, before it acts alone
3. Action whitelisting — only safe, reversible actions can be automated
4. Blast radius limits — cap how much it can scale/change at once
5. Human approval for high-impact actions (prod restarts, deletes)
6. Kill switch — instantly disable automation if it misbehaves
7. Continuous monitoring — track whether its actions actually help
```

The rule: an RL agent should never *explore* (try random actions) in production. It exploits its learned policy in production and only explores in safe environments.

---

## 🌍 When to Use RL vs Rules

| Use rule-based remediation | Use RL-based remediation |
|----------------------------|--------------------------|
| Well-understood, stable problems | Complex, changing environments |
| Small number of scenarios | Many interacting variables |
| Need full predictability | Can benefit from adaptation |
| Simpler to build and audit | Worth the complexity for scale |

**Reality:** Most organizations start with rules and only adopt RL for specific high-value, complex remediation scenarios where rules become unmanageable. RL remediation is advanced and relatively rare in production.

---

## 🎯 Interview Quick Points

- RL learns the best remediation *policy* through reward/penalty, not fixed rules
- Analogy: training a dog with treats — it learns which actions get rewarded
- Core concepts: agent, environment, state, action, reward, policy
- The **reward function** is the hardest part — must reward resolution AND penalize side effects/cost
- **Q-learning** maps state→action values, updated from outcomes
- Key advantage over rules: **adaptation** to changing conditions
- **Never explore (random actions) in production** — train offline/simulation first
- Deploy with guardrails: shadow mode, action whitelisting, blast-radius limits, human approval, kill switch
- Most orgs start with rules; RL is for complex, high-value scenarios
- Exploration vs exploitation trade-off is central to RL

## Next Steps

Continue to [MLOps-AIOps Integration](17-mlops-aiops-integration.md).
