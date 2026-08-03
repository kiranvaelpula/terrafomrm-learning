# Module 14: Helm Package Manager

## What is Helm?

Helm is the package manager for Kubernetes — like apt for Ubuntu or brew for macOS, but for Kubernetes applications. Instead of managing dozens of YAML files manually, Helm bundles them into a single "chart" that you can install with one command.

**When to use:**
- Installing third-party software (Prometheus, Nginx, PostgreSQL, Redis)
- Deploying your own app with different configs per environment (same chart, different values)
- Sharing reusable Kubernetes templates across teams
- Managing upgrades and rollbacks cleanly

**Key terms:**
- **Chart** — a package of Kubernetes YAML templates (like a .deb or .rpm)
- **Release** — an installed instance of a chart (you can install the same chart multiple times)
- **Values** — configuration that customizes the chart (like answers to a form)
- **Repository** — where charts are stored (like a package registry)

---

## 📦 Install Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version
```

---

## 🚀 Basic Commands

```bash
# Add a chart repository (like adding a package source)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Search for charts
helm search repo nginx
helm search hub wordpress          # Search all public repos

# Install a chart (creates a "release")
helm install my-release bitnami/nginx
helm install my-db bitnami/postgresql --set auth.postgresPassword=secretpassword

# List installed releases
helm list
helm list --all-namespaces

# See what values you can customize
helm show values bitnami/nginx

# Upgrade a release (change config or version)
helm upgrade my-release bitnami/nginx --set replicaCount=3

# Rollback to previous version
helm rollback my-release 1

# Uninstall
helm uninstall my-release
```

---

## 📝 Create Custom Chart

```bash
helm create mychart
```

This generates a chart structure:
```
mychart/
├── Chart.yaml          # Chart metadata (name, version, description)
├── values.yaml         # Default configuration values
├── templates/          # Kubernetes YAML templates
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── _helpers.tpl    # Template helper functions
└── charts/             # Dependencies (sub-charts)
```

**How templates work:**

values.yaml:
```yaml
replicaCount: 3
image:
  repository: nginx
  tag: "1.21"
```

templates/deployment.yaml:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
      - name: app
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

**In plain English:** Templates use `{{ }}` placeholders that get filled in with values. Same template, different values = different environments.

---

## 🎯 Install with Custom Values

```bash
# Override values at install time
helm install myapp ./mychart --set replicaCount=5

# Or use a values file
helm install myapp ./mychart -f production-values.yaml
```

production-values.yaml:
```yaml
replicaCount: 5
image:
  repository: myapp
  tag: "v2.0.0"
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
```

---

## Helm vs Plain YAML vs Kustomize

| Approach | Best for |
|---|---|
| Plain YAML | Simple apps, learning, one environment |
| Helm | Complex apps, third-party installs, multiple environments with very different configs |
| Kustomize | Slight variations between environments (patch-based) |

---

## Useful Commands

```bash
# See what Helm would generate (dry run)
helm template myapp ./mychart -f values.yaml

# Install but don't actually apply (preview)
helm install myapp ./mychart --dry-run --debug

# View release history
helm history my-release

# Download chart without installing (inspect it)
helm pull bitnami/nginx --untar
```

---

## ⏭️ Next: [Module 15: Monitoring & Logging](./15-monitoring-logging.md)
