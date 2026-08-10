# Advanced Scripting Patterns

> **Production-grade patterns for writing robust, maintainable, and scalable shell scripts. These patterns separate amateur scripts from professional ones.**

---

## 📖 Production Script Template

Every serious script should follow this structure:

```bash
#!/bin/bash
set -euo pipefail

# ============================================================
# Script: deploy.sh
# Purpose: Deploy application to target environment
# Author: DevOps Team
# Version: 2.1.0
# Usage: ./deploy.sh [OPTIONS] <environment>
# ============================================================

# ── Constants ──
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"
readonly VERSION="2.1.0"

# ── Colors (for terminal output) ──
if [[ -t 1 ]]; then   # Only if stdout is a terminal
  readonly RED='\033[0;31m'
  readonly GREEN='\033[0;32m'
  readonly YELLOW='\033[1;33m'
  readonly BLUE='\033[0;34m'
  readonly NC='\033[0m'
else
  readonly RED='' GREEN='' YELLOW='' BLUE='' NC=''
fi

# ── Logging ──
log_info()  { echo -e "${GREEN}[INFO]${NC}  $(date '+%H:%M:%S') $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $(date '+%H:%M:%S') $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $1" >&2; }
log_debug() { [[ "${VERBOSE:-false}" == "true" ]] && echo -e "${BLUE}[DEBUG]${NC} $1"; }
die()       { log_error "$1"; exit "${2:-1}"; }

# ── Usage/Help ──
usage() {
  cat << EOF
Usage: $SCRIPT_NAME [OPTIONS] <environment>

Deploy application to the specified environment.

Arguments:
  environment    Target environment (dev, staging, production)

Options:
  -h, --help       Show this help message
  -v, --verbose    Enable verbose/debug output
  -d, --dry-run    Show what would be done without doing it
  -V, --version    Show script version
  --no-color       Disable colored output

Examples:
  $SCRIPT_NAME dev
  $SCRIPT_NAME --verbose staging
  $SCRIPT_NAME --dry-run production
EOF
  exit 0
}

# ── Argument Parsing ──
VERBOSE=false
DRY_RUN=false
ENVIRONMENT=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)     usage ;;
    -v|--verbose)  VERBOSE=true; shift ;;
    -d|--dry-run)  DRY_RUN=true; shift ;;
    -V|--version)  echo "$SCRIPT_NAME v$VERSION"; exit 0 ;;
    --no-color)    RED=''; GREEN=''; YELLOW=''; BLUE=''; NC=''; shift ;;
    -*)            die "Unknown option: $1. Use --help for usage." ;;
    *)             ENVIRONMENT="$1"; shift ;;
  esac
done

# Validate required argument
[[ -n "$ENVIRONMENT" ]] || die "Environment argument required. Use --help."

# ── Cleanup ──
cleanup() {
  local exit_code=$?
  log_debug "Cleanup triggered (exit code: $exit_code)"
  rm -rf "${TEMP_DIR:-/tmp/nonexistent}"
  rm -f "${LOCK_FILE:-/tmp/nonexistent}"
  exit $exit_code
}
trap cleanup EXIT

# ── Error Handler ──
on_error() {
  log_error "Failed at line ${BASH_LINENO[0]}: ${BASH_COMMAND}"
}
trap on_error ERR

# ── Main Function ──
main() {
  log_info "Starting deployment to $ENVIRONMENT"
  log_debug "Script dir: $SCRIPT_DIR"
  log_debug "Dry run: $DRY_RUN"
  
  # ... your logic here ...
  
  log_info "✓ Deployment complete"
}

main "$@"
```

---

## 🔒 Locking (Prevent Multiple Instances)

When a script shouldn't run in parallel (like deployments or backups):

```bash
LOCK_FILE="/tmp/${SCRIPT_NAME}.lock"

acquire_lock() {
  if [ -f "$LOCK_FILE" ]; then
    local pid=$(cat "$LOCK_FILE")
    
    # Check if the process is actually still running
    if kill -0 "$pid" 2>/dev/null; then
      die "Another instance is running (PID: $pid). Lock file: $LOCK_FILE"
    else
      log_warn "Stale lock file found (PID $pid is dead). Removing."
      rm -f "$LOCK_FILE"
    fi
  fi
  
  # Create lock file with our PID
  echo $$ > "$LOCK_FILE"
  
  # Ensure lock is removed on exit
  trap "rm -f '$LOCK_FILE'" EXIT
  log_debug "Lock acquired (PID: $$)"
}

acquire_lock

# Better approach: Use flock (atomic file locking)
# In crontab: flock -n /tmp/backup.lock /opt/scripts/backup.sh
```

---

## ⚡ Parallel Execution

### Run tasks in parallel and collect results

```bash
#!/bin/bash
set -euo pipefail

servers=("web01" "web02" "web03" "web04" "web05")
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

deploy_to_server() {
  local server=$1
  local result_file="$TEMP_DIR/$server.result"
  
  # Simulate deployment
  echo "Deploying to $server..."
  if ssh deploy@$server "systemctl restart app" 2>/dev/null; then
    echo "SUCCESS" > "$result_file"
  else
    echo "FAILED" > "$result_file"
  fi
}

# Launch all deployments in parallel
for server in "${servers[@]}"; do
  deploy_to_server "$server" &
done

# Wait for all background jobs to complete
wait

# Collect results
echo ""
echo "=== Deployment Results ==="
failed=0
for server in "${servers[@]}"; do
  result=$(cat "$TEMP_DIR/$server.result" 2>/dev/null || echo "UNKNOWN")
  if [ "$result" = "SUCCESS" ]; then
    echo "  ✓ $server"
  else
    echo "  ✗ $server — $result"
    failed=$((failed + 1))
  fi
done

echo ""
echo "Total: ${#servers[@]} servers, $failed failed"
[ $failed -eq 0 ] || exit 1
```

### Limit parallel jobs (prevent overload)

```bash
MAX_PARALLEL=3
running=0

for server in "${servers[@]}"; do
  deploy_to_server "$server" &
  running=$((running + 1))
  
  # Wait when we hit the limit
  if [ $running -ge $MAX_PARALLEL ]; then
    wait -n           # Wait for ANY one to finish (bash 4.3+)
    running=$((running - 1))
  fi
done

wait    # Wait for remaining
```

---

## 📝 Configuration File Handling

### Read config from file

```bash
# config.env
# APP_NAME=myapp
# VERSION=2.0.1
# PORT=8080

# Load config safely
load_config() {
  local config_file=$1
  
  [ -f "$config_file" ] || die "Config not found: $config_file"
  
  # Source only valid KEY=VALUE lines (security: skip commands)
  while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ "$key" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$key" ]] && continue
    
    # Remove surrounding whitespace and quotes
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs | sed 's/^["'\'']//;s/["'\'']$//')
    
    # Export as environment variable
    export "$key=$value"
    log_debug "Config: $key=$value"
  done < "$config_file"
}

load_config "deploy.conf"
echo "Deploying $APP_NAME v$VERSION on port $PORT"
```

---

## 🔄 Signal Handling (Graceful Shutdown)

```bash
#!/bin/bash

RUNNING=true

# Handle Ctrl+C and kill gracefully
shutdown() {
  echo ""
  log_info "Shutdown signal received. Cleaning up..."
  RUNNING=false
  # Finish current task, then exit
}

trap shutdown SIGINT SIGTERM

# Main loop that can be interrupted gracefully
while $RUNNING; do
  echo "Processing... (Ctrl+C to stop gracefully)"
  
  # Do work here
  process_next_item
  
  sleep 5
done

log_info "Graceful shutdown complete"
```

---

## 📊 Progress Reporting

```bash
# Simple progress bar
progress_bar() {
  local current=$1
  local total=$2
  local width=50
  local percent=$((current * 100 / total))
  local filled=$((current * width / total))
  local empty=$((width - filled))
  
  printf "\r[%s%s] %d%% (%d/%d)" \
    "$(printf '#%.0s' $(seq 1 $filled))" \
    "$(printf '-%.0s' $(seq 1 $empty))" \
    "$percent" "$current" "$total"
}

# Usage
total=50
for ((i=1; i<=total; i++)); do
  progress_bar $i $total
  sleep 0.1    # Simulate work
done
echo ""    # New line after progress bar
```

---

## 🎯 Interview Quick Points

- Use a `main()` function to organize script entry point
- Parse arguments with `while` + `case` (supports long options)
- Lock files prevent concurrent execution (check if PID is alive)
- `trap cleanup EXIT` ensures cleanup always runs
- Use `flock` for atomic locking in cron jobs
- Run tasks in parallel with `&` and collect results with `wait`
- `${BASH_SOURCE[0]}` gives the script's real path (follows symlinks)
- `readonly` for constants prevents accidental modification
- Color output only when stdout is a terminal (`[[ -t 1 ]]`)
- Load config files carefully — don't blindly `source` them (security)
- Handle SIGINT/SIGTERM for graceful shutdown in long-running scripts
