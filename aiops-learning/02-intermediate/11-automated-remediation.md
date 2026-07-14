# Automated Remediation

## Learning Objectives
- Implement self-healing systems
- Automate incident response
- Build safe automation with guardrails
- Measure remediation effectiveness

---

## What is Automated Remediation?

Automated remediation enables systems to fix issues without human intervention:
- Restart failed services
- Scale resources automatically
- Clear caches
- Rollback bad deployments
- Reset connections

**Benefits:**
- Faster incident resolution (seconds vs minutes/hours)
- 24/7 coverage
- Consistent execution
- Reduced human error

---

## Simple Auto-Remediation

### Restart Failed Service

```python
import subprocess
import time

class ServiceRemediator:
    """Automatically remediate service failures"""
    
    def __init__(self, service_name):
        self.service_name = service_name
        self.restart_count = 0
        self.max_restarts = 3
        self.restart_window = 300  # 5 minutes
    
    def check_service_health(self):
        """Check if service is healthy"""
        try:
            response = requests.get(f'http://{self.service_name}:8080/health', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def restart_service(self):
        """Restart the service"""
        
        if self.restart_count >= self.max_restarts:
            self.escalate_to_human()
            return False
        
        print(f"Restarting {self.service_name}...")
        
        try:
            # Stop service
            subprocess.run(['systemctl', 'stop', self.service_name], check=True)
            time.sleep(5)
            
            # Start service
            subprocess.run(['systemctl', 'start', self.service_name], check=True)
            time.sleep(10)
            
            # Verify health
            if self.check_service_health():
                self.restart_count += 1
                self.log_remediation('restart', 'success')
                return True
            else:
                self.log_remediation('restart', 'failed')
                return False
                
        except Exception as e:
            self.log_remediation('restart', 'error', str(e))
            return False
    
    def escalate_to_human(self):
        """Escalate to on-call engineer"""
        send_alert(f"Service {self.service_name} failed {self.restart_count} times. Manual intervention needed.")
    
    def log_remediation(self, action, status, details=''):
        """Log remediation action"""
        log_entry = {
            'timestamp': datetime.now(),
            'service': self.service_name,
            'action': action,
            'status': status,
            'details': details
        }
        save_to_log(log_entry)

# Usage
remediator = ServiceRemediator('payment-service')

if not remediator.check_service_health():
    remediator.restart_service()
```

---

## Advanced Auto-Remediation Framework

### Complete Remediation System

```python
from enum import Enum
from dataclasses import dataclass
from typing import Callable, List
import asyncio

class RemediationAction(Enum):
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    CLEAR_CACHE = "clear_cache"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    KILL_PROCESS = "kill_process"
    RESET_CONNECTION = "reset_connection"

@dataclass
class RemediationRule:
    """Define remediation rule"""
    name: str
    condition: Callable
    action: RemediationAction
    params: dict
    safety_check: Callable = None
    max_attempts: int = 3
    cooldown_minutes: int = 10

class AutoRemediationEngine:
    """Intelligent auto-remediation engine"""
    
    def __init__(self):
        self.rules = []
        self.execution_history = []
        self.safety_mode = True
    
    def add_rule(self, rule: RemediationRule):
        """Add remediation rule"""
        self.rules.append(rule)
    
    async def evaluate_and_execute(self, incident):
        """Evaluate incident and execute remediation"""
        
        for rule in self.rules:
            if rule.condition(incident):
                # Check if safe to execute
                if self.safety_mode and rule.safety_check:
                    if not rule.safety_check(incident):
                        self.log_skip(rule, "Safety check failed")
                        continue
                
                # Check execution history
                if not self.can_execute(rule):
                    self.log_skip(rule, "Rate limit exceeded")
                    continue
                
                # Execute remediation
                result = await self.execute_action(rule, incident)
                
                self.record_execution(rule, result)
                
                if result['success']:
                    return result
        
        return {'success': False, 'reason': 'No applicable rule found'}
    
    def can_execute(self, rule: RemediationRule):
        """Check if rule can be executed (rate limiting)"""
        
        recent_executions = [
            ex for ex in self.execution_history
            if ex['rule'] == rule.name and
            (datetime.now() - ex['timestamp']).seconds < rule.cooldown_minutes * 60
        ]
        
        return len(recent_executions) < rule.max_attempts
    
    async def execute_action(self, rule: RemediationRule, incident):
        """Execute remediation action"""
        
        print(f"Executing remediation: {rule.name}")
        
        try:
            if rule.action == RemediationAction.RESTART_SERVICE:
                return await self.restart_service(rule.params)
            
            elif rule.action == RemediationAction.SCALE_UP:
                return await self.scale_up(rule.params)
            
            elif rule.action == RemediationAction.CLEAR_CACHE:
                return await self.clear_cache(rule.params)
            
            elif rule.action == RemediationAction.ROLLBACK_DEPLOYMENT:
                return await self.rollback_deployment(rule.params)
            
            else:
                return {'success': False, 'reason': 'Unknown action'}
                
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    async def restart_service(self, params):
        """Restart service"""
        service = params['service']
        
        # Implementation
        await asyncio.sleep(2)  # Simulate restart
        
        return {
            'success': True,
            'action': 'restart',
            'service': service,
            'message': f'Service {service} restarted successfully'
        }
    
    async def scale_up(self, params):
        """Scale up resources"""
        service = params['service']
        replicas = params['replicas']
        
        # Kubernetes example
        cmd = f"kubectl scale deployment {service} --replicas={replicas}"
        
        result = subprocess.run(cmd.split(), capture_output=True)
        
        if result.returncode == 0:
            return {
                'success': True,
                'action': 'scale_up',
                'service': service,
                'replicas': replicas
            }
        
        return {'success': False, 'reason': result.stderr.decode()}
    
    async def clear_cache(self, params):
        """Clear cache"""
        cache_key = params.get('key', '*')
        
        # Redis example
        import redis
        r = redis.Redis()
        
        if cache_key == '*':
            r.flushall()
        else:
            r.delete(cache_key)
        
        return {
            'success': True,
            'action': 'clear_cache',
            'key': cache_key
        }
    
    async def rollback_deployment(self, params):
        """Rollback to previous version"""
        service = params['service']
        
        # Kubernetes rollback
        cmd = f"kubectl rollout undo deployment/{service}"
        
        result = subprocess.run(cmd.split(), capture_output=True)
        
        return {
            'success': result.returncode == 0,
            'action': 'rollback',
            'service': service
        }
    
    def record_execution(self, rule, result):
        """Record execution for rate limiting"""
        self.execution_history.append({
            'rule': rule.name,
            'timestamp': datetime.now(),
            'result': result
        })
    
    def log_skip(self, rule, reason):
        """Log skipped execution"""
        print(f"Skipped {rule.name}: {reason}")

# Define remediation rules
engine = AutoRemediationEngine()

# Rule 1: Restart on high error rate
engine.add_rule(RemediationRule(
    name="restart_on_errors",
    condition=lambda incident: incident['error_rate'] > 0.1,
    action=RemediationAction.RESTART_SERVICE,
    params={'service': 'payment-service'},
    safety_check=lambda incident: incident['error_rate'] < 0.5,  # Don't restart if >50% errors
    max_attempts=3,
    cooldown_minutes=10
))

# Rule 2: Scale up on high CPU
engine.add_rule(RemediationRule(
    name="scale_on_cpu",
    condition=lambda incident: incident.get('cpu_usage', 0) > 80,
    action=RemediationAction.SCALE_UP,
    params={'service': 'api-gateway', 'replicas': 5},
    max_attempts=2,
    cooldown_minutes=15
))

# Execute remediation
incident = {
    'service': 'payment-service',
    'error_rate': 0.15,
    'cpu_usage': 75
}

result = asyncio.run(engine.evaluate_and_execute(incident))
print(result)
```

---

## Safety Guardrails

```python
class SafetyGuard:
    """Safety checks for auto-remediation"""
    
    @staticmethod
    def check_blast_radius(action, params):
        """Ensure action doesn't affect too many resources"""
        
        if action == RemediationAction.RESTART_SERVICE:
            # Don't restart critical services during business hours
            if is_business_hours() and params['service'] in ['payment', 'auth']:
                return False
        
        return True
    
    @staticmethod
    def check_recent_changes(service):
        """Don't auto-remediate if recent deployment"""
        
        last_deployment = get_last_deployment_time(service)
        
        if (datetime.now() - last_deployment).seconds < 600:  # 10 minutes
            return False
        
        return True
    
    @staticmethod
    def require_approval(action):
        """Some actions require human approval"""
        
        high_risk_actions = [
            RemediationAction.ROLLBACK_DEPLOYMENT,
            RemediationAction.KILL_PROCESS
        ]
        
        return action in high_risk_actions
```

---

**Next**: [Capacity Planning →](12-capacity-planning.md)
