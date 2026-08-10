# Shell Scripts in CI/CD

> **Shell scripts are the glue in CI/CD pipelines — build, test, deploy, validate, rollback. Every Jenkins/GitHub Actions/GitLab CI pipeline relies on shell.**

---

## 📖 Why Shell in CI/CD?

CI/CD systems execute shell commands at every step. Even if you use YAML-based pipeline configs, they ultimately run shell commands. Understanding how to write reliable CI/CD scripts is essential.

```
┌─────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline                         │
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐  │
│  │  Build  │──│  Test   │──│ Publish │──│  Deploy  │  │
│  │(script) │  │(script) │  │(script) │  │ (script) │  │
│  └─────────┘  └─────────┘  └─────────┘  └──────────┘  │
│                                                          │
│  Each box = a shell script or shell commands             │
└─────────────────────────────────────────────────────────┘
```

---

## 🏗️ Build Script

```bash
#!/bin/bash
set -euo pipefail

# ── CI Environment Variables (provided by CI system) ──
BUILD_NUMBER="${BUILD_NUMBER:-local}"
GIT_COMMIT="${GIT_COMMIT:-$(git rev-parse HEAD)}"
GIT_BRANCH="${GIT_BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
GIT_SHORT="${GIT_COMMIT:0:7}"

echo "═══════════════════════════════════"
echo "  Build #${BUILD_NUMBER}"
echo "  Branch: ${GIT_BRANCH}"
echo "  Commit: ${GIT_SHORT}"
echo "═══════════════════════════════════"

# ── Install Dependencies ──
echo "▶ Installing dependencies..."
npm ci --production=false          # ci = clean install (exact versions)

# ── Lint ──
echo "▶ Running linter..."
npm run lint || {
  echo "❌ Linting failed. Fix style issues before merging."
  exit 1
}

# ── Build Application ──
echo "▶ Building application..."
npm run build

# ── Generate Build Info ──
cat > build-info.json << EOF
{
  "build": "${BUILD_NUMBER}",
  "commit": "${GIT_COMMIT}",
  "branch": "${GIT_BRANCH}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "builder": "$(hostname)"
}
EOF

echo "✓ Build complete"
echo "  Artifact: build-info.json"
cat build-info.json
```

---

## 🧪 Test Script

```bash
#!/bin/bash
set -euo pipefail

echo "═══════════════════════════════════"
echo "  Running Tests"
echo "═══════════════════════════════════"

# ── Unit Tests ──
echo "▶ Unit tests..."
npm test -- --coverage --ci --reporters=default --reporters=jest-junit

# Check coverage threshold
COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
echo "  Coverage: ${COVERAGE}%"

THRESHOLD=80
if (( $(echo "$COVERAGE < $THRESHOLD" | bc -l) )); then
  echo "❌ Coverage ${COVERAGE}% is below threshold ${THRESHOLD}%"
  exit 1
fi
echo "  ✓ Coverage meets threshold"

# ── Integration Tests (if not PR) ──
if [ "${GIT_BRANCH}" != "feature/"* ]; then
  echo "▶ Integration tests..."
  
  # Start test dependencies
  docker-compose -f docker-compose.test.yml up -d
  
  # Wait for DB to be ready
  echo "  Waiting for test database..."
  timeout 30 bash -c 'until docker-compose exec -T db pg_isready; do sleep 1; done'
  
  # Run integration tests
  npm run test:integration
  
  # Cleanup
  docker-compose -f docker-compose.test.yml down -v
fi

echo "✓ All tests passed"
```

---

## 🐳 Docker Build and Push Script

```bash
#!/bin/bash
set -euo pipefail

# ── Variables ──
REGISTRY="${DOCKER_REGISTRY:-registry.example.com}"
IMAGE_NAME="${APP_NAME:-myapp}"
IMAGE_TAG="${BUILD_NUMBER:-latest}-${GIT_COMMIT:0:7}"
FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "═══════════════════════════════════"
echo "  Docker Build & Push"
echo "  Image: ${FULL_IMAGE}"
echo "═══════════════════════════════════"

# ── Build ──
echo "▶ Building Docker image..."
docker build \
  --build-arg BUILD_NUMBER="$BUILD_NUMBER" \
  --build-arg GIT_COMMIT="$GIT_COMMIT" \
  --label "build.number=$BUILD_NUMBER" \
  --label "git.commit=$GIT_COMMIT" \
  -t "$FULL_IMAGE" \
  -t "${REGISTRY}/${IMAGE_NAME}:latest" \
  .

# ── Security Scan ──
echo "▶ Scanning image for vulnerabilities..."
if command -v trivy &>/dev/null; then
  trivy image --exit-code 1 --severity HIGH,CRITICAL "$FULL_IMAGE" || {
    echo "⚠️  Vulnerabilities found! Review before deploying to production."
    # Don't fail build for staging, only warn
    [ "${ENVIRONMENT:-}" = "production" ] && exit 1
  }
fi

# ── Push ──
echo "▶ Pushing to registry..."
docker push "$FULL_IMAGE"
docker push "${REGISTRY}/${IMAGE_NAME}:latest"

echo "✓ Image pushed: $FULL_IMAGE"

# ── Output for next stage ──
echo "IMAGE_TAG=${IMAGE_TAG}" >> "${GITHUB_ENV:-/dev/null}"    # GitHub Actions
echo "IMAGE_TAG=${IMAGE_TAG}" > build.env                       # Generic
```

---

## 🚀 Deploy Script

```bash
#!/bin/bash
set -euo pipefail

# ── Arguments ──
ENVIRONMENT=${1:?"Usage: $0 <environment> <image_tag>"}
IMAGE_TAG=${2:?"Usage: $0 <environment> <image_tag>"}
NAMESPACE="${ENVIRONMENT}"
APP_NAME="${APP_NAME:-myapp}"
REGISTRY="${DOCKER_REGISTRY:-registry.example.com}"
FULL_IMAGE="${REGISTRY}/${APP_NAME}:${IMAGE_TAG}"

echo "═══════════════════════════════════"
echo "  Deploying to ${ENVIRONMENT}"
echo "  Image: ${FULL_IMAGE}"
echo "═══════════════════════════════════"

# ── Pre-deploy Validation ──
echo "▶ Validating..."

# Check image exists in registry
if ! docker manifest inspect "$FULL_IMAGE" &>/dev/null; then
  echo "❌ Image not found in registry: $FULL_IMAGE"
  exit 1
fi

# Check kubectl connectivity
kubectl cluster-info --context "$ENVIRONMENT" &>/dev/null || {
  echo "❌ Cannot connect to $ENVIRONMENT cluster"
  exit 1
}

# ── Deploy ──
echo "▶ Updating deployment..."
kubectl set image deployment/${APP_NAME} \
  ${APP_NAME}=${FULL_IMAGE} \
  -n ${NAMESPACE}

# ── Wait for Rollout ──
echo "▶ Waiting for rollout..."
if ! kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE} --timeout=300s; then
  echo "❌ Rollout failed! Rolling back..."
  kubectl rollout undo deployment/${APP_NAME} -n ${NAMESPACE}
  kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE} --timeout=120s
  echo "  Rollback complete"
  exit 1
fi

# ── Post-deploy Health Check ──
echo "▶ Running health checks..."
sleep 10     # Give pods time to fully start

HEALTH_URL="https://${ENVIRONMENT}.example.com/health"
max_attempts=5
attempt=1

while [ $attempt -le $max_attempts ]; do
  status=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 5 "$HEALTH_URL" || echo "000")
  
  if [ "$status" = "200" ]; then
    echo "  ✓ Health check passed (attempt $attempt)"
    break
  fi
  
  echo "  Attempt $attempt/$max_attempts — status $status, retrying..."
  sleep 5
  attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
  echo "❌ Health check failed after $max_attempts attempts! Rolling back..."
  kubectl rollout undo deployment/${APP_NAME} -n ${NAMESPACE}
  exit 1
fi

echo "✓ Deployment successful!"
echo "  Environment: ${ENVIRONMENT}"
echo "  Image: ${IMAGE_TAG}"
echo "  URL: https://${ENVIRONMENT}.example.com"
```

---

## 🔧 CI/CD Helper Scripts

### Version Bumping

```bash
#!/bin/bash
# Auto-increment version based on commit messages
set -euo pipefail

CURRENT=$(cat VERSION || echo "0.0.0")
IFS='.' read -r major minor patch <<< "$CURRENT"

# Check commit messages for version indicators
if git log --oneline -1 | grep -qi "breaking\|major"; then
  major=$((major + 1)); minor=0; patch=0
elif git log --oneline -1 | grep -qi "feat\|feature\|minor"; then
  minor=$((minor + 1)); patch=0
else
  patch=$((patch + 1))
fi

NEW_VERSION="${major}.${minor}.${patch}"
echo "$NEW_VERSION" > VERSION
echo "Version bumped: $CURRENT → $NEW_VERSION"
```

### Changelog Generator

```bash
#!/bin/bash
# Generate changelog from git commits
set -euo pipefail

LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
RANGE="${LAST_TAG:+$LAST_TAG..}HEAD"

echo "# Changelog"
echo ""
echo "## $(date +%Y-%m-%d)"
echo ""

# Features
features=$(git log $RANGE --oneline --grep="feat" 2>/dev/null || true)
if [ -n "$features" ]; then
  echo "### Features"
  echo "$features" | sed 's/^/- /'
  echo ""
fi

# Fixes
fixes=$(git log $RANGE --oneline --grep="fix" 2>/dev/null || true)
if [ -n "$fixes" ]; then
  echo "### Bug Fixes"
  echo "$fixes" | sed 's/^/- /'
fi
```

---

## 📋 CI/CD Script Best Practices

| Practice | Why |
|----------|-----|
| Always `set -euo pipefail` | Fail fast on errors |
| Use `${VAR:?message}` for required vars | Clear error if CI var is missing |
| Echo what you're doing | Makes CI logs readable |
| Add timing info | Know where time is spent |
| Exit with meaningful codes | CI knows pass/fail |
| Use `--ci` flags on tools | Optimized for non-interactive |
| Cache dependencies | Faster builds |
| Health check after deploy | Verify deployment actually works |
| Auto-rollback on failure | Don't leave broken state |
| Tag images with commit hash | Traceability |

---

## 🎯 Interview Quick Points

- CI/CD scripts MUST use `set -euo pipefail`
- Use CI environment variables (`$BUILD_NUMBER`, `$GIT_COMMIT`, `$BRANCH_NAME`)
- Include health checks after deployment
- Auto-rollback on failure (`kubectl rollout undo`)
- Exit with non-zero code to fail the pipeline stage
- Docker images should be tagged with build number + commit hash
- Security scanning (trivy, snyk) before pushing images
- Scripts should be idempotent (safe to re-run)
- Use `timeout` for operations that might hang
- Output variables for next stages (`>> $GITHUB_ENV`)
- Always validate before deploying (image exists, cluster reachable)
