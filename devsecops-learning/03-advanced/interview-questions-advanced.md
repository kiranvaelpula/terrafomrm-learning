# DevSecOps Interview Questions - Advanced Level

Advanced interview questions covering enterprise security architecture, threat modeling, compliance, supply chain security, and building security culture at scale.

---

## Enterprise Security Architecture

### Q1: Design a comprehensive DevSecOps architecture for a global enterprise with multiple teams and cloud providers.

**Answer:**

**Architecture Components:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer Workstation                     │
├─────────────────────────────────────────────────────────────┤
│  IDE Plugins │ Pre-commit Hooks │ Local SAST │ Git-Secrets │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Source Control (Git)                    │
├─────────────────────────────────────────────────────────────┤
│  Branch Protection │ Signed Commits │ CODEOWNERS │ Audit Log│
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      CI/CD Pipeline                          │
├─────────────────────────────────────────────────────────────┤
│  SAST │ SCA │ Secret Scan │ Container Scan │ IaC Security   │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Artifact Registry                         │
├─────────────────────────────────────────────────────────────┤
│  Image Signing │ SBOM │ Vulnerability DB │ Access Control   │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Multi-Cloud Deployment                       │
├─────────────────────────────────────────────────────────────┤
│  AWS │ Azure │ GCP │ On-Prem │ Policy Enforcement │ CSPM    │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Runtime Security & Monitoring                   │
├─────────────────────────────────────────────────────────────┤
│  CWPP │ WAF │ API Gateway │ SIEM │ Threat Intelligence      │
└─────────────────────────────────────────────────────────────┘
```

**Implementation Details:**

**1. Source Control Security:**
```yaml
# GitHub Advanced Security configuration
github_security:
  secret_scanning:
    enabled: true
    partner_patterns: true
    custom_patterns:
      - name: "Internal API Keys"
        regex: "INTERNAL_KEY_[A-Z0-9]{32}"
  
  code_scanning:
    enabled: true
    default_setup: true
    tools:
      - codeql
      - semgrep
  
  dependency_review:
    enabled: true
    fail_on: "critical"
  
  branch_protection:
    required_reviews: 2
    required_signatures: true
    require_code_owner_reviews: true
    dismiss_stale_reviews: true
```

**2. Centralized Security Platform:**
```python
# security_platform.py - Unified security orchestration
from typing import List, Dict
import asyncio

class SecurityOrchestrator:
    def __init__(self):
        self.scanners = {
            'sast': SemgrepScanner(),
            'sca': SnykScanner(),
            'secrets': TruffleHogScanner(),
            'container': TrivyScanner(),
            'iac': CheckovScanner(),
            'dast': ZAPScanner()
        }
        
        self.policy_engine = OPAPolicyEngine()
        self.vuln_db = VulnerabilityDatabase()
        self.notification_service = NotificationService()
    
    async def scan_pipeline(self, context: Dict) -> Dict:
        """Orchestrate all security scans"""
        results = {}
        
        # Run scans in parallel
        scan_tasks = [
            self._run_scanner(name, scanner, context)
            for name, scanner in self.scanners.items()
            if self._should_run_scanner(name, context)
        ]
        
        scan_results = await asyncio.gather(*scan_tasks)
        
        # Aggregate results
        for name, result in zip(self.scanners.keys(), scan_results):
            results[name] = result
        
        # Evaluate policies
        policy_decision = await self.policy_engine.evaluate(results)
        
        # Enrich with threat intelligence
        enriched = await self._enrich_findings(results)
        
        # Deduplicate and prioritize
        prioritized = await self._prioritize_findings(enriched)
        
        # Create tickets for critical issues
        if policy_decision['block_deployment']:
            await self._create_blocking_issues(prioritized)
        
        # Send notifications
        await self.notification_service.notify(prioritized)
        
        return {
            'scan_results': results,
            'policy_decision': policy_decision,
            'findings': prioritized
        }
    
    async def _prioritize_findings(self, findings: List[Dict]) -> List[Dict]:
        """Prioritize vulnerabilities using CVSS + context"""
        for finding in findings:
            # Base CVSS score
            base_score = finding.get('cvss', 0)
            
            # Contextual factors
            if finding.get('exploitable'):
                base_score += 2
            
            if finding.get('internet_facing'):
                base_score += 1
            
            if finding.get('contains_pii'):
                base_score += 1.5
            
            if finding.get('has_public_exploit'):
                base_score += 2
            
            finding['priority_score'] = min(base_score, 10)
            finding['priority'] = self._score_to_priority(base_score)
        
        return sorted(findings, key=lambda x: x['priority_score'], reverse=True)
    
    def _score_to_priority(self, score: float) -> str:
        if score >= 9:
            return 'P0-Critical'
        elif score >= 7:
            return 'P1-High'
        elif score >= 4:
            return 'P2-Medium'
        else:
            return 'P3-Low'
```

**3. Policy as Code Framework:**
```rego
# policies/deployment_security.rego
package deployment.security

import data.kubernetes
import data.compliance

# Deny deployments without security context
deny[msg] {
    input.kind == "Deployment"
    not input.spec.template.spec.securityContext
    msg := "Deployment must specify securityContext"
}

# Enforce image scanning
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not has_valid_scan_attestation(container.image)
    msg := sprintf("Image %v must have valid security scan", [container.image])
}

# Require signed images in production
deny[msg] {
    input.metadata.namespace == "production"
    container := input.spec.template.spec.containers[_]
    not is_image_signed(container.image)
    msg := sprintf("Production image %v must be signed", [container.image])
}

# Compliance checks
deny[msg] {
    input.kind == "Deployment"
    violations := compliance.check_pci_dss(input)
    count(violations) > 0
    msg := sprintf("PCI-DSS violations: %v", [violations])
}

# Helper functions
has_valid_scan_attestation(image) {
    attestation := data.attestations[image]
    attestation.scan_date > time.now_ns() - (7 * 24 * 60 * 60 * 1000000000)
    attestation.critical_vulns == 0
}

is_image_signed(image) {
    signature := data.signatures[image]
    signature.verified == true
    signature.signer in data.trusted_signers
}
```

**4. Multi-Cloud Security Posture Management:**
```python
# cspm.py - Cloud Security Posture Management
class CloudSecurityPosture:
    def __init__(self):
        self.providers = {
            'aws': AWSSecurityCheck(),
            'azure': AzureSecurityCheck(),
            'gcp': GCPSecurityCheck()
        }
    
    async def assess_posture(self) -> Dict:
        """Assess security across all cloud providers"""
        results = {}
        
        for provider_name, provider in self.providers.items():
            results[provider_name] = await provider.assess({
                'checks': [
                    'encryption_at_rest',
                    'encryption_in_transit',
                    'public_access',
                    'iam_policies',
                    'network_security',
                    'logging_monitoring',
                    'vulnerability_management',
                    'backup_recovery'
                ]
            })
        
        # Generate compliance report
        compliance_score = self._calculate_compliance_score(results)
        
        return {
            'assessment': results,
            'compliance_score': compliance_score,
            'recommendations': self._generate_recommendations(results)
        }
```

**Key Architectural Decisions:**

1. **Centralized Security Platform**: Single pane of glass
2. **Policy as Code**: Consistent enforcement
3. **Automated Remediation**: Reduce MTTR
4. **Continuous Compliance**: Real-time monitoring
5. **Developer Self-Service**: Shift-left with guardrails

---

### Q2: How do you implement zero-trust security in a microservices architecture?

**Answer:**

**Zero Trust Principles for Microservices:**

1. **Never Trust, Always Verify**
2. **Assume Breach**
3. **Verify Explicitly**
4. **Least Privilege Access**
5. **Micro-Segmentation**

**Implementation:**

**1. Service Mesh with mTLS:**
```yaml
# Istio PeerAuthentication - enforce mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT  # Require mTLS for all traffic
---
# Authorization Policy - fine-grained access control
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-service-authz
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/order-service"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/charge"]
    when:
    - key: request.headers[x-request-id]
      notValues: [""]
```

**2. Workload Identity:**
```python
# workload_identity.py
from google.auth import compute_engine
from google.cloud import secretmanager

class WorkloadIdentityManager:
    def __init__(self):
        self.credentials = compute_engine.Credentials()
        self.secret_client = secretmanager.SecretManagerServiceClient(
            credentials=self.credentials
        )
    
    def get_service_credentials(self, service_name: str) -> Dict:
        """Get credentials based on workload identity"""
        # Service account automatically injected by GKE
        # No long-lived credentials needed
        
        secret_name = f"projects/my-project/secrets/{service_name}-creds/versions/latest"
        response = self.secret_client.access_secret_version(name=secret_name)
        
        return json.loads(response.payload.data.decode('UTF-8'))
```

**3. API Gateway with AuthN/AuthZ:**
```yaml
# Kong API Gateway configuration
services:
  - name: payment-api
    url: http://payment-service:8080
    routes:
      - name: charge-route
        paths:
          - /api/payments/charge
    plugins:
      # JWT authentication
      - name: jwt
        config:
          key_claim_name: kid
          secret_is_base64: false
      
      # Rate limiting per consumer
      - name: rate-limiting
        config:
          minute: 100
          policy: local
      
      # Request validation
      - name: request-validator
        config:
          body_schema: |
            {
              "type": "object",
              "required": ["amount", "currency"],
              "properties": {
                "amount": {"type": "number", "minimum": 0},
                "currency": {"type": "string", "enum": ["USD", "EUR"]}
              }
            }
      
      # OPA policy enforcement
      - name: opa
        config:
          policy: |
            package kong
            
            default allow = false
            
            allow {
              input.request.http.method == "POST"
              has_valid_jwt
              not exceeds_transaction_limit
            }
```

**4. Network Segmentation:**
```yaml
# Calico NetworkPolicy - microsegmentation
apiVersion: projectcalico.org/v3
kind: NetworkPolicy
metadata:
  name: payment-service-policy
  namespace: production
spec:
  selector: app == 'payment-service'
  types:
    - Ingress
    - Egress
  
  ingress:
    # Only allow from order-service
    - action: Allow
      source:
        selector: app == 'order-service'
      destination:
        ports:
          - 8080
  
  egress:
    # Only allow to database
    - action: Allow
      destination:
        selector: app == 'postgres'
        ports:
          - 5432
    
    # Allow DNS
    - action: Allow
      destination:
        ports:
          - 53
```

**5. Runtime Security Monitoring:**
```python
# runtime_security.py - Detect anomalous behavior
class RuntimeSecurityMonitor:
    def __init__(self):
        self.baseline_behaviors = {}
        self.alert_threshold = 0.8
    
    async def monitor_service(self, service_name: str):
        """Monitor service behavior for anomalies"""
        while True:
            metrics = await self._collect_metrics(service_name)
            
            # Check for anomalies
            anomalies = self._detect_anomalies(service_name, metrics)
            
            if anomalies:
                await self._handle_anomalies(service_name, anomalies)
            
            await asyncio.sleep(60)
    
    def _detect_anomalies(self, service_name: str, metrics: Dict) -> List:
        """Detect deviations from baseline"""
        anomalies = []
        baseline = self.baseline_behaviors.get(service_name, {})
        
        # Check network connections
        if metrics['outbound_connections'] != baseline.get('expected_connections', []):
            anomalies.append({
                'type': 'unexpected_network_connection',
                'details': metrics['outbound_connections']
            })
        
        # Check file access
        if metrics['file_access_paths'] - baseline.get('expected_files', set()):
            anomalies.append({
                'type': 'unexpected_file_access',
                'details': list(metrics['file_access_paths'])
            })
        
        # Check process execution
        if metrics['spawned_processes']:
            anomalies.append({
                'type': 'process_execution',
                'details': metrics['spawned_processes']
            })
        
        return anomalies
    
    async def _handle_anomalies(self, service_name: str, anomalies: List):
        """Respond to detected anomalies"""
        severity = self._calculate_severity(anomalies)
        
        if severity >= self.alert_threshold:
            # Critical anomaly - take action
            await self._isolate_workload(service_name)
            await self._trigger_incident_response(service_name, anomalies)
        else:
            # Log for investigation
            await self._log_anomaly(service_name, anomalies)
```

**Benefits of Zero Trust:**
- Eliminates implicit trust
- Reduces blast radius
- Better visibility
- Compliance alignment
- Defense in depth

---

## Threat Modeling & Risk Assessment

### Q3: Walk through a comprehensive threat modeling exercise for a cloud-native application.

**Answer:**

**STRIDE Threat Modeling Framework:**

**Phase 1: System Decomposition**

```python
# threat_model.py
from dataclasses import dataclass
from typing import List, Set
from enum import Enum

class AssetType(Enum):
    DATA = "data"
    SERVICE = "service"
    IDENTITY = "identity"
    INFRASTRUCTURE = "infrastructure"

class ThreatCategory(Enum):
    SPOOFING = "Spoofing identity"
    TAMPERING = "Tampering with data"
    REPUDIATION = "Repudiation"
    INFORMATION_DISCLOSURE = "Information disclosure"
    DENIAL_OF_SERVICE = "Denial of service"
    ELEVATION_OF_PRIVILEGE = "Elevation of privilege"

@dataclass
class Asset:
    name: str
    type: AssetType
    sensitivity: str  # public, internal, confidential, restricted
    data_classification: str
    compliance_requirements: List[str]

@dataclass
class DataFlow:
    source: str
    destination: str
    protocol: str
    data_classification: str
    encrypted: bool
    authenticated: bool

@dataclass
class TrustBoundary:
    name: str
    description: str
    crossed_by: List[DataFlow]

class ThreatModel:
    def __init__(self, application_name: str):
        self.application_name = application_name
        self.assets: List[Asset] = []
        self.data_flows: List[DataFlow] = []
        self.trust_boundaries: List[TrustBoundary] = []
        self.threats: List[Dict] = []
    
    def add_asset(self, asset: Asset):
        self.assets.append(asset)
    
    def analyze_threats(self) -> List[Dict]:
        """Analyze system for STRIDE threats"""
        threats = []
        
        # Analyze each data flow
        for flow in self.data_flows:
            # Spoofing

            if not flow.authenticated:
                threats.append({
                    'category': ThreatCategory.SPOOFING,
                    'description': f"Unauthenticated flow from {flow.source} to {flow.destination}",
                    'severity': 'HIGH' if flow.data_classification == 'confidential' else 'MEDIUM',
                    'mitigation': 'Implement mutual TLS authentication'
                })
            
            # Tampering
            if not flow.encrypted:
                threats.append({
                    'category': ThreatCategory.TAMPERING,
                    'description': f"Unencrypted data flow: {flow.source} → {flow.destination}",
                    'severity': 'CRITICAL' if flow.data_classification == 'restricted' else 'HIGH',
                    'mitigation': 'Enable TLS 1.3 encryption'
                })
            
            # Information Disclosure
            for boundary in self.trust_boundaries:
                if flow in boundary.crossed_by and not flow.encrypted:
                    threats.append({
                        'category': ThreatCategory.INFORMATION_DISCLOSURE,
                        'description': f"Data crosses trust boundary '{boundary.name}' without encryption",
                        'severity': 'CRITICAL',
                        'mitigation': 'Encrypt data at rest and in transit'
                    })
        
        # Analyze assets
        for asset in self.assets:
            if asset.sensitivity in ['confidential', 'restricted']:
                # Check if asset has proper controls
                if not self._has_access_controls(asset):
                    threats.append({
                        'category': ThreatCategory.ELEVATION_OF_PRIVILEGE,
                        'description': f"Sensitive asset '{asset.name}' lacks access controls",
                        'severity': 'HIGH',
                        'mitigation': 'Implement RBAC and least privilege'
                    })
        
        return threats
    
    def generate_report(self) -> str:
        """Generate threat modeling report"""
        threats = self.analyze_threats()
        
        report = f"""
# Threat Model Report: {self.application_name}

## Executive Summary
- Total Threats Identified: {len(threats)}
- Critical: {len([t for t in threats if t['severity'] == 'CRITICAL'])}
- High: {len([t for t in threats if t['severity'] == 'HIGH'])}
- Medium: {len([t for t in threats if t['severity'] == 'MEDIUM'])}

## Assets
"""
        for asset in self.assets:
            report += f"\n- {asset.name} ({asset.type.value}) - {asset.sensitivity}"
        
        report += "\n\n## Identified Threats\n"
        
        for i, threat in enumerate(threats, 1):
            report += f"""
### {i}. {threat['category'].value}
- **Description**: {threat['description']}
- **Severity**: {threat['severity']}
- **Mitigation**: {threat['mitigation']}
"""
        
        return report

# Example usage
model = ThreatModel("E-commerce Application")

# Define assets
model.add_asset(Asset(
    name="Customer Database",
    type=AssetType.DATA,
    sensitivity="restricted",
    data_classification="PII",
    compliance_requirements=["PCI-DSS", "GDPR"]
))

model.add_asset(Asset(
    name="Payment Service",
    type=AssetType.SERVICE,
    sensitivity="confidential",
    data_classification="Financial",
    compliance_requirements=["PCI-DSS"]
))

# Define data flows
model.data_flows.append(DataFlow(
    source="Web Frontend",
    destination="Payment Service",
    protocol="HTTPS",
    data_classification="confidential",
    encrypted=True,
    authenticated=True
))

# Analyze
report = model.generate_report()
print(report)
```

**Phase 2: Attack Tree Analysis**

```
Goal: Steal Customer Payment Data
├── Attack Vector 1: Exploit API Vulnerability
│   ├── Find SQL Injection
│   │   ├── Automated Scanner [HIGH probability, LOW skill]
│   │   └── Manual Testing [MEDIUM probability, MEDIUM skill]
│   ├── Exploit XXE
│   └── Bypass Authentication
│       ├── Credential Stuffing [MEDIUM probability, LOW skill]
│       └── Session Hijacking [LOW probability, HIGH skill]
│
├── Attack Vector 2: Compromise Infrastructure
│   ├── Container Escape
│   │   ├── Exploit Kernel Vulnerability [LOW probability, HIGH skill]
│   │   └── Misconfigured Capabilities [MEDIUM probability, MEDIUM skill]
│   ├── Kubernetes API Abuse
│   └── Cloud Account Compromise
│
└── Attack Vector 3: Supply Chain Attack
    ├── Malicious Dependency
    ├── Compromised Build Pipeline
    └── Insider Threat
```

**Phase 3: Risk Rating (DREAD)**

```python
def calculate_dread_score(threat: Dict) -> Dict:
    """Calculate DREAD score"""
    # Damage potential (1-10)
    damage = threat.get('damage', 5)
    
    # Reproducibility (1-10)
    reproducibility = threat.get('reproducibility', 5)
    
    # Exploitability (1-10)
    exploitability = threat.get('exploitability', 5)
    
    # Affected users (1-10)
    affected_users = threat.get('affected_users', 5)
    
    # Discoverability (1-10)
    discoverability = threat.get('discoverability', 5)
    
    dread_score = (damage + reproducibility + exploitability + 
                   affected_users + discoverability) / 5
    
    return {
        'dread_score': dread_score,
        'risk_level': 'CRITICAL' if dread_score >= 8 else 
                     'HIGH' if dread_score >= 6 else
                     'MEDIUM' if dread_score >= 4 else 'LOW',
        'components': {
            'damage': damage,
            'reproducibility': reproducibility,
            'exploitability': exploitability,
            'affected_users': affected_users,
            'discoverability': discoverability
        }
    }

# Example threat assessment
threat = {
    'name': 'SQL Injection in Payment API',
    'damage': 10,  # Can steal all customer data
    'reproducibility': 8,  # Easy to reproduce
    'exploitability': 6,  # Requires some knowledge
    'affected_users': 10,  # All users affected
    'discoverability': 7  # Can be found with automated tools
}

risk = calculate_dread_score(threat)
print(f"DREAD Score: {risk['dread_score']}")
print(f"Risk Level: {risk['risk_level']}")
```

---

## Supply Chain Security

### Q4: How do you secure the software supply chain from development to deployment?

**Answer:**

**Supply Chain Security Framework:**

**1. Source Code Integrity:**
```yaml
# .github/workflows/supply-chain-security.yml
name: Supply Chain Security

on: [push, pull_request]

jobs:
  verify-commits:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Verify signed commits
        run: |
          # Ensure all commits are signed
          unsigned=$(git log --pretty="%H %G?" origin/main..HEAD | grep -v " G$" || true)
          if [ -n "$unsigned" ]; then
            echo "Unsigned commits found:"
            echo "$unsigned"
            exit 1
          fi
      
      - name: Check commit authors
        run: |
          # Verify commits from approved authors
          git log --format="%ae" origin/main..HEAD | \
          while read email; do
            if ! grep -q "$email" .github/APPROVED_AUTHORS; then
              echo "Unauthorized author: $email"
              exit 1
            fi
          done
  
  sbom-generation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          format: cyclonedx-json
          output-file: sbom.json
      
      - name: Sign SBOM
        run: |
          cosign sign-blob --key cosign.key sbom.json > sbom.json.sig
      
      - name: Upload SBOM
        uses: actions/upload-artifact@v3
        with:
          name: sbom
          path: |
            sbom.json
            sbom.json.sig
  
  dependency-verification:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Verify dependency checksums
        run: |
          # For npm
          npm ci --ignore-scripts
          
          # Verify lock file integrity
          if ! git diff --exit-code package-lock.json; then
            echo "Lock file mismatch!"
            exit 1
          fi
      
      - name: Check for malicious packages
        run: |
          # Use socket.dev or similar
          npx socket-security@latest ci
      
      - name: License compliance
        run: |
          npx license-checker --summary --onlyAllow "MIT;Apache-2.0;BSD-3-Clause"
```

**2. Build Provenance:**
```python
# generate_provenance.py - SLSA provenance
from in_toto import runlib, verifylib
from datetime import datetime
import json

class ProvenanceGenerator:
    def __init__(self):
        self.slsa_version = "0.2"
    
    def generate_provenance(self, build_info: Dict) -> Dict:
        """Generate SLSA provenance"""
        provenance = {
            "_type": "https://in-toto.io/Statement/v0.1",
            "subject": [{
                "name": build_info['artifact_name'],
                "digest": {
                    "sha256": build_info['artifact_sha256']
                }
            }],
            "predicateType": "https://slsa.dev/provenance/v0.2",
            "predicate": {
                "builder": {
                    "id": build_info['builder_id']
                },
                "buildType": build_info['build_type'],
                "invocation": {
                    "configSource": {
                        "uri": build_info['repo_uri'],
                        "digest": {
                            "sha1": build_info['commit_sha']
                        },
                        "entryPoint": build_info['workflow_file']
                    }
                },
                "buildConfig": build_info['build_config'],
                "metadata": {
                    "buildStartedOn": build_info['start_time'],
                    "buildFinishedOn": datetime.utcnow().isoformat() + "Z",
                    "completeness": {
                        "parameters": True,
                        "environment": True,
                        "materials": True
                    },
                    "reproducible": build_info.get('reproducible', False)
                },
                "materials": build_info['dependencies']
            }
        }
        
        return provenance
    
    def sign_provenance(self, provenance: Dict, key_path: str) -> str:
        """Sign provenance with Sigstore"""
        import subprocess
        
        # Write provenance to temp file
        with open('/tmp/provenance.json', 'w') as f:
            json.dump(provenance, f)
        
        # Sign with cosign
        result = subprocess.run([
            'cosign', 'sign-blob',
            '--key', key_path,
            '/tmp/provenance.json'
        ], capture_output=True, text=True)
        
        return result.stdout

# Usage in CI/CD
build_info = {
    'artifact_name': 'myapp',
    'artifact_sha256': 'abc123...',
    'builder_id': 'https://github.com/actions',
    'build_type': 'https://github.com/actions/workflow@v1',
    'repo_uri': 'https://github.com/myorg/myapp',
    'commit_sha': 'def456...',
    'workflow_file': '.github/workflows/build.yml',
    'build_config': {...},
    'start_time': '2026-07-14T10:00:00Z',
    'dependencies': [...]
}

generator = ProvenanceGenerator()
provenance = generator.generate_provenance(build_info)
signature = generator.sign_provenance(provenance, 'signing-key.pem')
```

**3. Container Image Signing:**
```bash
# Sign container images with Sigstore
#!/bin/bash

IMAGE="myapp:v1.2.3"
REGISTRY="ghcr.io/myorg"

# Build image
docker build -t $REGISTRY/$IMAGE .

# Generate SBOM
syft $REGISTRY/$IMAGE -o cyclonedx-json > sbom.json

# Scan for vulnerabilities
grype $REGISTRY/$IMAGE --fail-on high

# Sign image
cosign sign --key cosign.key $REGISTRY/$IMAGE

# Attach SBOM to image
cosign attach sbom --sbom sbom.json $REGISTRY/$IMAGE

# Attach attestation
cosign attest --key cosign.key --predicate provenance.json $REGISTRY/$IMAGE

# Push to registry
docker push $REGISTRY/$IMAGE

# Verify (deployment time)
cosign verify --key cosign.pub $REGISTRY/$IMAGE
cosign verify-attestation --key cosign.pub $REGISTRY/$IMAGE
```

**4. Admission Control:**
```yaml
# Kyverno policy - verify signed images
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-images
spec:
  validationFailureAction: enforce
  rules:
  - name: verify-signature
    match:
      any:
      - resources:
          kinds:
          - Pod
    verifyImages:
    - imageReferences:
      - "ghcr.io/myorg/*"
      attestors:
      - count: 1
        entries:
        - keys:
            publicKeys: |-
              -----BEGIN PUBLIC KEY-----
              MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...
              -----END PUBLIC KEY-----
      attestations:
      - predicateType: https://slsa.dev/provenance/v0.2
        conditions:
        - all:
          - key: "{{ builder.id }}"
            operator: Equals
            value: "https://github.com/actions"
```

**5. Dependency Management:**
```python
# dependency_monitor.py
class DependencyMonitor:
    def __init__(self):
        self.vuln_db = VulnerabilityDatabase()
        self.approved_licenses = ['MIT', 'Apache-2.0', 'BSD-3-Clause']
    
    def analyze_dependencies(self, lockfile: str) -> Dict:
        """Analyze dependencies for security and compliance"""
        results = {
            'vulnerabilities': [],
            'license_violations': [],
            'outdated': [],
            'typosquatting_risks': []
        }
        
        dependencies = self._parse_lockfile(lockfile)
        
        for dep in dependencies:
            # Check for vulnerabilities
            vulns = self.vuln_db.query(dep['name'], dep['version'])
            results['vulnerabilities'].extend(vulns)
            
            # Check license compliance
            if dep['license'] not in self.approved_licenses:
                results['license_violations'].append(dep)
            
            # Check if outdated
            latest = self._get_latest_version(dep['name'])
            if self._is_outdated(dep['version'], latest):
                results['outdated'].append({
                    'package': dep['name'],
                    'current': dep['version'],
                    'latest': latest
                })
            
            # Check for typosquatting
            if self._is_potential_typosquat(dep['name']):
                results['typosquatting_risks'].append(dep)
        
        return results
    
    def _is_potential_typosquat(self, package_name: str) -> bool:
        """Detect potential typosquatting"""
        popular_packages = ['express', 'react', 'lodash', 'axios']
        
        for popular in popular_packages:
            # Calculate Levenshtein distance
            distance = self._levenshtein_distance(package_name, popular)
            if 0 < distance <= 2:  # Similar but not exact
                return True
        
        return False
```

---

## Compliance & Governance

### Q5: Design a compliance-as-code framework for SOC 2, PCI-DSS, and HIPAA.

**Answer:**

**Multi-Framework Compliance System:**

```python
# compliance_framework.py
from abc import ABC, abstractmethod
from typing import List, Dict
from enum import Enum

class ComplianceFramework(Enum):
    SOC2 = "SOC 2"
    PCI_DSS = "PCI-DSS"
    HIPAA = "HIPAA"
    GDPR = "GDPR"
    ISO27001 = "ISO 27001"

class ControlCategory(Enum):
    ACCESS_CONTROL = "Access Control"
    ENCRYPTION = "Encryption"
    LOGGING = "Logging & Monitoring"
    NETWORK_SECURITY = "Network Security"
    VULNERABILITY_MANAGEMENT = "Vulnerability Management"
    INCIDENT_RESPONSE = "Incident Response"
    DATA_PROTECTION = "Data Protection"

class ComplianceControl(ABC):
    def __init__(self, control_id: str, description: str, 
                 frameworks: List[ComplianceFramework]):
        self.control_id = control_id
        self.description = description
        self.frameworks = frameworks
    
    @abstractmethod
    async def check(self, context: Dict) -> Dict:
        """Check if control is satisfied"""
        pass

class EncryptionAtRestControl(ComplianceControl):
    def __init__(self):
        super().__init__(
            control_id="ENC-001",
            description="Data must be encrypted at rest",
            frameworks=[
                ComplianceFramework.SOC2,
                ComplianceFramework.PCI_DSS,
                ComplianceFramework.HIPAA
            ]
        )
    
    async def check(self, context: Dict) -> Dict:
        """Verify encryption at rest"""
        results = {
            'compliant': True,
            'violations': [],
            'evidence': []
        }
        
        # Check databases
        for db in context.get('databases', []):
            if not db.get('encryption_enabled'):
                results['compliant'] = False
                results['violations'].append({
                    'resource': db['name'],
                    'issue': 'Encryption at rest not enabled',
                    'severity': 'CRITICAL',
                    'remediation': f"Enable encryption for {db['name']}"
                })
            else:
                results['evidence'].append({
                    'resource': db['name'],
                    'proof': f"Encryption enabled with {db['encryption_type']}"
                })
        
        # Check S3 buckets
        for bucket in context.get('s3_buckets', []):
            if not bucket.get('encryption'):
                results['compliant'] = False
                results['violations'].append({
                    'resource': bucket['name'],
                    'issue': 'S3 bucket not encrypted',
                    'severity': 'HIGH'
                })
        
        return results

class AccessControlControl(ComplianceControl):
    def __init__(self):
        super().__init__(
            control_id="AC-001",
            description="Implement least privilege access control",
            frameworks=[
                ComplianceFramework.SOC2,
                ComplianceFramework.PCI_DSS,
                ComplianceFramework.HIPAA
            ]
        )
    
    async def check(self, context: Dict) -> Dict:
        """Verify access controls"""
        results = {
            'compliant': True,
            'violations': [],
            'evidence': []
        }
        
        # Check IAM policies
        for policy in context.get('iam_policies', []):
            # Check for overly permissive actions
            if '*' in policy.get('actions', []):
                results['compliant'] = False
                results['violations'].append({
                    'resource': policy['name'],
                    'issue': 'Wildcard actions in IAM policy',
                    'severity': 'HIGH',
                    'remediation': 'Use specific actions instead of *'
                })
            
            # Check for overly broad resources
            if policy.get('resources') == ['*']:
                results['compliant'] = False
                results['violations'].append({
                    'resource': policy['name'],
                    'issue': 'Policy applies to all resources',
                    'severity': 'MEDIUM',
                    'remediation': 'Scope policy to specific resources'
                })
        
        # Check MFA enforcement
        for user in context.get('users', []):
            if user.get('has_console_access') and not user.get('mfa_enabled'):
                results['compliant'] = False
                results['violations'].append({
                    'resource': user['name'],
                    'issue': 'MFA not enabled for console access',
                    'severity': 'HIGH',
                    'remediation': f"Enable MFA for user {user['name']}"
                })
        
        return results

class AuditLoggingControl(ComplianceControl):
    def __init__(self):
        super().__init__(
            control_id="LOG-001",
            description="Enable comprehensive audit logging",
            frameworks=[
                ComplianceFramework.SOC2,
                ComplianceFramework.PCI_DSS,
                ComplianceFramework.HIPAA
            ]
        )
    
    async def check(self, context: Dict) -> Dict:
        """Verify audit logging"""
        results = {
            'compliant': True,
            'violations': [],
            'evidence': []
        }
        
        # Check CloudTrail
        cloudtrail = context.get('cloudtrail', {})
        if not cloudtrail.get('enabled'):
            results['compliant'] = False
            results['violations'].append({
                'resource': 'CloudTrail',
                'issue': 'CloudTrail not enabled',
                'severity': 'CRITICAL',
                'remediation': 'Enable CloudTrail in all regions'
            })
        elif not cloudtrail.get('log_file_validation'):
            results['compliant'] = False
            results['violations'].append({
                'resource': 'CloudTrail',
                'issue': 'Log file validation not enabled',
                'severity': 'HIGH',
                'remediation': 'Enable log file validation'
            })
        
        # Check log retention
        if cloudtrail.get('retention_days', 0) < 90:
            results['compliant'] = False
            results['violations'].append({
                'resource': 'CloudTrail',
                'issue': f"Log retention too short: {cloudtrail.get('retention_days')} days",
                'severity': 'MEDIUM',
                'remediation': 'Set retention to at least 90 days'
            })
        
        return results

class ComplianceEngine:
    def __init__(self):
        self.controls: List[ComplianceControl] = [
            EncryptionAtRestControl(),
            AccessControlControl(),
            AuditLoggingControl(),
            # Add more controls...
        ]
    
    async def assess_compliance(self, context: Dict, 
                               framework: ComplianceFramework) -> Dict:
        """Assess compliance for specific framework"""
        results = {
            'framework': framework.value,
            'assessment_date': datetime.utcnow().isoformat(),
            'controls_checked': 0,
            'controls_passed': 0,
            'controls_failed': 0,
            'critical_violations': 0,
            'high_violations': 0,
            'medium_violations': 0,
            'details': []
        }
        
        # Check relevant controls
        for control in self.controls:
            if framework in control.frameworks:
                results['controls_checked'] += 1
                
                check_result = await control.check(context)
                
                if check_result['compliant']:
                    results['controls_passed'] += 1
                else:
                    results['controls_failed'] += 1
                    
                    # Count violations by severity
                    for violation in check_result['violations']:
                        if violation['severity'] == 'CRITICAL':
                            results['critical_violations'] += 1
                        elif violation['severity'] == 'HIGH':
                            results['high_violations'] += 1
                        elif violation['severity'] == 'MEDIUM':
                            results['medium_violations'] += 1
                
                results['details'].append({
                    'control_id': control.control_id,
                    'description': control.description,
                    'compliant': check_result['compliant'],
                    'violations': check_result['violations'],
                    'evidence': check_result['evidence']
                })
        
        # Calculate compliance score
        if results['controls_checked'] > 0:
            results['compliance_score'] = (
                results['controls_passed'] / results['controls_checked'] * 100
            )
        else:
            results['compliance_score'] = 0
        
        return results
    
    def generate_report(self, assessment_results: Dict) -> str:
        """Generate compliance report"""
        report = f"""
# Compliance Assessment Report
## Framework: {assessment_results['framework']}
## Date: {assessment_results['assessment_date']}

### Summary
- **Compliance Score**: {assessment_results['compliance_score']:.1f}%
- **Controls Checked**: {assessment_results['controls_checked']}
- **Controls Passed**: {assessment_results['controls_passed']}
- **Controls Failed**: {assessment_results['controls_failed']}

### Violations by Severity
- **Critical**: {assessment_results['critical_violations']}
- **High**: {assessment_results['high_violations']}
- **Medium**: {assessment_results['medium_violations']}

### Detailed Findings
"""
        
        for detail in assessment_results['details']:
            status = "✅ PASS" if detail['compliant'] else "❌ FAIL"
            report += f"""
#### {detail['control_id']}: {detail['description']} {status}
"""
            
            if not detail['compliant']:
                report += "\n**Violations:**\n"
                for violation in detail['violations']:
                    report += f"""
- **{violation['severity']}**: {violation['issue']}
  - Resource: {violation['resource']}
  - Remediation: {violation['remediation']}
"""
        
        return report

# Usage
async def run_compliance_check():
    # Collect system context
    context = {
        'databases': await collect_database_info(),
        's3_buckets': await collect_s3_info(),
        'iam_policies': await collect_iam_info(),
        'users': await collect_user_info(),
        'cloudtrail': await collect_cloudtrail_info()
    }
    
    engine = ComplianceEngine()
    
    # Assess SOC 2 compliance
    soc2_results = await engine.assess_compliance(context, ComplianceFramework.SOC2)
    report = engine.generate_report(soc2_results)
    
    print(report)
    
    # Generate attestation if compliant
    if soc2_results['compliance_score'] >= 95:
        generate_compliance_attestation(soc2_results)
```

**Automated Remediation:**

```python
#