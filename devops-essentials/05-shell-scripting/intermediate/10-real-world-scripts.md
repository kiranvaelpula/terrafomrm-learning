# Real-World DevOps Scripts

> **Practical shell scripts used daily in DevOps — deployment, monitoring, backup, and automation. These are production-ready patterns you can adapt.**

---

## 📖 Why Real-World Scripts?

Interview questions often ask: "Write a script that does X." These are the common patterns every DevOps engineer should know by heart.

---

## 🚀 Script 1: Application Deployment

```bash
#!/bin/bash
set -euo pipefail

# ══════════════════════════════════════════
# Deployment Script
# Usage: ./deploy.sh <environment> <version>
# ══════════════════════════════════════════

# ── Configuration ──
APP_NAME="my-webapp"
DEPLOY_USER="deploy"
LOG="/var/log/deployments/${APP_NAME}.log"

declare -A SERVERS
SERVERS[dev]="10.0.1.10"
SERVERS[staging]="10.0.2.10 10.0.2.11"
SERVERS[prod]="10.0.3.10 10.0.3.11 10.0.3.12 10.0.3.13"

# ── Functions ──
log() { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG"; }
die() { log "FATAL: $1"; exit 1; }

usage() {
  echo "Usage: $0 <environment> <version>"
  echo "  Environments: dev, staging, prod"
  echo "  Example: $0 staging v2.0.1"
  exit 1
}

deploy_to_server() {
  local server=$1
  local version=$2
  
  log "  → Deploying to $server..."
  
  ssh ${DEPLOY_USER}@${server} << EOF
    set -e
    cd /opt/${APP_NAME}
    
    # Create backup
    cp -r current current.bak.\$(date +%Y%m%d_%H%M%S)
    
    # Download new version
    wget -q "https://releases.example.com/${APP_NAME}/${version}.tar.gz" -O /tmp/release.tar.gz
    
    # Extract and switch
    mkdir -p releases/${version}
    tar -xzf /tmp/release.tar.gz -C releases/${version}
    
    # Switch symlink (atomic operation)
    ln -sfn releases/${version} current
    
    # Restart service
    sudo systemctl restart ${APP_NAME}
    
    # Quick health check
    sleep 3
    curl -sf http://localhost:8080/health > /dev/null || exit 1
EOF

  if [ $? -eq 0 ]; then
    log "  ✓ $server deployed successfully"
    return 0
  else
    log "  ✗ $server FAILED"
    return 1
  fi
}

# ── Validation ──
[ $# -eq 2 ] || usage
ENVIRONMENT=$1
VERSION=$2

[ -n "${SERVERS[$ENVIRONMENT]:-}" ] || die "Unknown environment: $ENVIRONMENT"

# Production needs confirmation
if [ "$ENVIRONMENT" = "prod" ]; then
  read -p "⚠️  Deploy $VERSION to PRODUCTION? (yes/no): " confirm
  [ "$confirm" = "yes" ] || die "Deployment cancelled"
fi

# ── Main Deployment ──
log "═══ Deploying $APP_NAME $VERSION to $ENVIRONMENT ═══"

failed=0
for server in ${SERVERS[$ENVIRONMENT]}; do
  if ! deploy_to_server "$server" "$VERSION"; then
    failed=$((failed + 1))
  fi
done

# ── Summary ──
if [ $failed -eq 0 ]; then
  log "═══ ✓ Deployment SUCCESSFUL ═══"
else
  log "═══ ✗ $failed server(s) FAILED ═══"
  exit 1
fi
```

---

## 💾 Script 2: Automated Backup with Rotation

```bash
#!/bin/bash
set -euo pipefail

# ══════════════════════════════════════════
# Backup Script — Database + Files
# Runs daily via cron
# ══════════════════════════════════════════

# ── Configuration ──
BACKUP_ROOT="/backups"
DB_NAME="production_db"
DB_USER="backup_user"
DB_HOST="db.internal"
APP_DIR="/opt/myapp/data"
RETENTION_DAYS=30
S3_BUCKET="s3://company-backups/daily"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

# ── Functions ──
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }
die() { log "ERROR: $1"; exit 1; }

# Cleanup trap
cleanup() {
  if [ "${BACKUP_FAILED:-false}" = "true" ]; then
    log "Backup failed — cleaning up partial backup"
    rm -rf "$BACKUP_DIR"
  fi
}
trap cleanup EXIT

notify() {
  local status=$1
  local message=$2
  # Send to Slack
  curl -sf -X POST "$SLACK_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"$status Backup: $message\"}" || true
}

# ── Pre-checks ──
log "═══ Starting backup ═══"
BACKUP_FAILED=true    # Will set to false on success

mkdir -p "$BACKUP_DIR" || die "Cannot create backup directory"
command -v mysqldump &>/dev/null || die "mysqldump not found"
command -v aws &>/dev/null || die "AWS CLI not found"

# Check disk space (need at least 10GB free)
free_space=$(df -BG "$BACKUP_ROOT" | awk 'NR==2{print int($4)}')
if [ $free_space -lt 10 ]; then
  die "Not enough disk space: ${free_space}GB free (need 10GB)"
fi

# ── Database Backup ──
log "Backing up database: $DB_NAME..."
mysqldump -h "$DB_HOST" -u "$DB_USER" --single-transaction \
  "$DB_NAME" | gzip > "${BACKUP_DIR}/${DB_NAME}.sql.gz"
log "  Database backup: $(du -h "${BACKUP_DIR}/${DB_NAME}.sql.gz" | cut -f1)"

# ── Application Files ──
log "Backing up application data..."
tar -czf "${BACKUP_DIR}/app_data.tar.gz" -C "$APP_DIR" .
log "  App data backup: $(du -h "${BACKUP_DIR}/app_data.tar.gz" | cut -f1)"

# ── Upload to S3 ──
log "Uploading to S3..."
aws s3 sync "$BACKUP_DIR" "${S3_BUCKET}/${TIMESTAMP}/" --quiet
log "  S3 upload complete"

# ── Rotate Old Backups ──
log "Cleaning backups older than ${RETENTION_DAYS} days..."
deleted=$(find "$BACKUP_ROOT" -maxdepth 1 -type d -mtime +$RETENTION_DAYS -print -exec rm -rf {} \; | wc -l)
log "  Removed $deleted old backup(s)"

# ── Success ──
BACKUP_FAILED=false
total_size=$(du -sh "$BACKUP_DIR" | cut -f1)
log "═══ ✓ Backup complete: $total_size ═══"
notify "✅" "Backup successful (${total_size})"
```

---

## 📊 Script 3: Server Health Monitor

```bash
#!/bin/bash
set -euo pipefail

# ══════════════════════════════════════════
# Health Monitor
# Checks CPU, memory, disk, services
# ══════════════════════════════════════════

HOSTNAME=$(hostname)
ALERT_EMAIL="devops@example.com"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# Thresholds
CPU_WARN=70
CPU_CRIT=90
MEM_WARN=80
MEM_CRIT=95
DISK_WARN=75
DISK_CRIT=90

SERVICES=("nginx" "docker" "postgresql")

alerts=()

# ── Check CPU ──
cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print int($2 + $4)}')
if [ $cpu -gt $CPU_CRIT ]; then
  alerts+=("🔴 CPU CRITICAL: ${cpu}%")
elif [ $cpu -gt $CPU_WARN ]; then
  alerts+=("🟡 CPU WARNING: ${cpu}%")
fi

# ── Check Memory ──
mem=$(free | awk '/Mem/{printf("%.0f"), $3/$2*100}')
if [ $mem -gt $MEM_CRIT ]; then
  alerts+=("🔴 MEMORY CRITICAL: ${mem}%")
elif [ $mem -gt $MEM_WARN ]; then
  alerts+=("🟡 MEMORY WARNING: ${mem}%")
fi

# ── Check Disk ──
while IFS= read -r line; do
  partition=$(echo "$line" | awk '{print $6}')
  usage=$(echo "$line" | awk '{print int($5)}')
  
  if [ $usage -gt $DISK_CRIT ]; then
    alerts+=("🔴 DISK CRITICAL: $partition at ${usage}%")
  elif [ $usage -gt $DISK_WARN ]; then
    alerts+=("🟡 DISK WARNING: $partition at ${usage}%")
  fi
done < <(df -h | grep '^/dev')

# ── Check Services ──
for svc in "${SERVICES[@]}"; do
  if ! systemctl is-active --quiet "$svc" 2>/dev/null; then
    alerts+=("🔴 SERVICE DOWN: $svc")
  fi
done

# ── Send Alerts ──
if [ ${#alerts[@]} -gt 0 ]; then
  message="⚠️ *Server Alert: $HOSTNAME*\n"
  for alert in "${alerts[@]}"; do
    message+="• $alert\n"
  done
  
  echo -e "$message"
  
  # Slack alert
  if [ -n "$SLACK_WEBHOOK" ]; then
    curl -sf -X POST "$SLACK_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{\"text\":\"$(echo -e "$message")\"}" || true
  fi
else
  echo "[$(date '+%H:%M:%S')] All checks OK — CPU:${cpu}% MEM:${mem}%"
fi
```

---

## 🔧 Script 4: Log Rotation and Cleanup

```bash
#!/bin/bash
set -euo pipefail

# ══════════════════════════════════════════
# Log Rotation Script
# Compresses old logs, removes ancient ones
# ══════════════════════════════════════════

LOG_DIRS=(
  "/var/log/myapp"
  "/var/log/nginx"
  "/opt/app/logs"
)

COMPRESS_AFTER_DAYS=1     # Compress logs older than 1 day
DELETE_AFTER_DAYS=30      # Delete logs older than 30 days
MAX_LOG_SIZE="100M"       # Rotate if larger than 100MB

log() { echo "[$(date '+%H:%M:%S')] $1"; }

for dir in "${LOG_DIRS[@]}"; do
  [ -d "$dir" ] || continue
  log "Processing: $dir"
  
  # Compress old uncompressed logs
  compressed=0
  while IFS= read -r file; do
    gzip "$file"
    compressed=$((compressed + 1))
  done < <(find "$dir" -name "*.log" -mtime +$COMPRESS_AFTER_DAYS -not -name "*.gz")
  [ $compressed -gt 0 ] && log "  Compressed $compressed file(s)"
  
  # Delete ancient compressed logs
  deleted=$(find "$dir" -name "*.gz" -mtime +$DELETE_AFTER_DAYS -delete -print | wc -l)
  [ $deleted -gt 0 ] && log "  Deleted $deleted old archive(s)"
  
  # Rotate oversized active logs
  while IFS= read -r file; do
    mv "$file" "${file}.$(date +%Y%m%d_%H%M%S)"
    touch "$file"    # Create new empty log
    log "  Rotated oversized: $(basename $file)"
  done < <(find "$dir" -name "*.log" -size +$MAX_LOG_SIZE)
done

log "✓ Log maintenance complete"
```

---

## 🎯 Key Patterns Across All Scripts

| Pattern | Why |
|---------|-----|
| `set -euo pipefail` | Catch errors immediately |
| `trap cleanup EXIT` | Always clean up temp files |
| `log()` function | Consistent timestamped output |
| `die()` function | Fail with clear message |
| Validation at start | Fail fast with helpful errors |
| `$?` check after critical ops | Know exactly what failed |
| Confirmation for destructive ops | Safety for production |
| Slack/email notifications | Team awareness |
| Retry logic | Handle transient failures |
| Lock files | Prevent concurrent runs |

---

## 🎯 Interview Quick Points

- Production scripts always use `set -euo pipefail`
- Add logging with timestamps for auditability
- Include health checks after deployments
- Implement rollback on failure
- Clean up old files to prevent disk issues
- Use functions for reusable, testable logic
- Validate inputs and prerequisites before doing work
- Notify the team on success AND failure
- Use lock files to prevent parallel execution conflicts
- Test scripts in dev/staging before running in production
