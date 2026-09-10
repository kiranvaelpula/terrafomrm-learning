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

## 📖 Understanding Helm (Intuition First)

Installing a real application on Kubernetes rarely means one YAML file. A typical app needs a Deployment, a Service, a ConfigMap, a Secret, an Ingress, maybe an HPA and some RBAC — a dozen interlocking manifests. Applying and maintaining all of those by hand, keeping them consistent across dev, staging, and prod, is tedious and error-prone. **Helm is the package manager that bundles all those files into one installable unit**, exactly the way `apt` or `brew` bundle a program and its dependencies so you install with a single command.

The core idea is **templating plus configuration**. A Helm **chart** is a set of YAML templates with `{{ }}` placeholders instead of hard-coded values. A **values file** supplies the actual numbers and names to fill in. This means one chart can produce completely different deployments just by swapping values — 2 replicas and a debug image for dev, 10 replicas and a production image for prod, from the exact same templates. You stop copy-pasting near-identical YAML and start parameterizing it.

When you install a chart, Helm creates a **release** — a named, tracked instance of that chart in your cluster. This is powerful because Helm remembers the history of each release. Upgrading is one command, and if the new version misbehaves, `helm rollback` snaps you back to the previous working state instantly. Helm turns "edit a pile of YAML and hope" into versioned, reversible deployments.

Helm also transformed how you consume third-party software. Want Prometheus, PostgreSQL, or an NGINX ingress controller? Instead of hunting down and stitching together their manifests, you add a **repository** and `helm install` a maintained, battle-tested chart in seconds. This ecosystem of shareable charts is a huge part of why Helm became the de facto standard.

It's worth knowing where Helm fits among alternatives. Plain YAML is fine for simple, single-environment apps. **Kustomize** is great when environments differ only slightly (it patches a base). **Helm** shines when you need real templating logic, dependency management, packaging for distribution, or clean upgrade/rollback of complex applications. Understanding charts, values, and releases is the mental model that makes Helm click.

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

## 🎯 Interview Quick Points

- **Helm** is the Kubernetes package manager — like apt/brew but for bundles of K8s manifests
- Key terms: **Chart** (templated package), **Release** (an installed instance), **Values** (config), **Repository** (chart source)
- Core power is **templating + values** — one chart produces different deployments per environment
- Templates use `{{ .Values.x }}`, `{{ .Release.Name }}` placeholders filled from `values.yaml` or `--set`
- Helm tracks **release history**, enabling clean `helm upgrade` and instant `helm rollback`
- Great for installing maintained third-party software (Prometheus, PostgreSQL, ingress-nginx) in seconds
- Chart structure: `Chart.yaml` (metadata), `values.yaml` (defaults), `templates/` (manifests), `charts/` (dependencies)
- Override config with `--set key=value` or a custom `-f values.yaml` file
- Preview output without applying via `helm template` or `helm install --dry-run --debug`
- Helm 3 is **tiller-less** (no server-side component), improving security over Helm 2
- Choosing tools: plain YAML (simple), **Kustomize** (patch-based small variations), **Helm** (templating, packaging, complex apps)

---

## ⏭️ Next: [Module 15: Monitoring & Logging](./15-monitoring-logging.md)
