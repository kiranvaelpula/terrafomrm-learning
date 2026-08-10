# Error Handling and Debugging

> **Production scripts must handle errors gracefully and be easy to debug when things go wrong. A script that silently fails is worse than one that crashes loudly.**

---

## 📖 Why Error Handling Matters

Without error handling:
```bash
#!/bin/bash
cd /opt/app              # What if this fails? Script continues with WRONG directory!
rm -rf *                 # Deletes files from wherever we ARE (maybe /)
git pull                 # Fails silently
systemctl restart app    # Restarts wrong thing or fails
echo "Done!"             # Reports success even when everything failed
```

With error handling:
```bash
#!/bin/bash
set -euo pipefail

cd /opt/app || die "Cannot find /opt/app"
git pull || die "Git pull failed"
systemctl restart app || die "Service restart failed"
echo "Done!"             # Only prints if everything actually succeeded
```

---

## 🛡️ Strict Mode: set -euo pipefail

This is the single most important line in production scripts:

```bash
#!/bin/bash
set -euo pipefail
```

Let's break down what each flag does:

### `set -e` — Exit immediately on error

```bash
# WITHOUT set -e:
#!/bin/bash
false                    # This fails (exit code 1)
echo "Still running!"   # This STILL executes — dangerous!

# WITH set -e:
#!/bin/bash
set -e
false                    # This fails
echo "Never reaches here"   # Script already exited
```

**Exceptions where `set -e` doesn't trigger:**
```bash
set -e

# These DON'T cause exit (by design):
if ! command_that_might_fail; then    # In if condition — fine
  echo "It failed, handling it"
fi

command_that_might_fail || true        # OR with true — suppresses
command_that_might_fail || handle_error # OR with handler — fine

count=$(grep -c "pattern" file.txt || true)   # May return 1 if no match
```

### `set -u` — Error on undefined variables

```bash
# WITHOUT set -u:
#!/bin/bash
echo "Hello $NAEM"       # Typo! $NAEM is undefined → empty string, no error
rm -rf "/$UNDEFINED/"    # Would try to delete root!

# WITH set -u:
#!/bin/bash
set -u
echo "Hello $NAEM"       # ERROR: NAEM: unbound variable (script exits)
```

**How to use default values with set -u:**
```bash
set -u

# These work safely with set -u:
echo "${NAME:-default_value}"    # Use default if NAME is unset
echo "${PORT:=8080}"             # Set to 8080 if unset

# Check if variable is set
if [ -n "${MY_VAR:-}" ]; then    # :-} provides empty default
  echo "MY_VAR is set to $MY_VAR"
fi
```

### `set -o pipefail` — Pipe fails if ANY command fails

```bash
# WITHOUT pipefail:
#!/bin/bash
cat /nonexistent/file | grep "pattern" | wc -l
echo $?    # 0 (success!) — because wc succeeded, even though cat failed

# WITH pipefail:
#!/bin/bash
set -o pipefail
cat /nonexistent/file | grep "pattern" | wc -l
echo $?    # 1 (failure!) — because cat failed
```

---

## 🔧 Error Handling Patterns

### Pattern 1: OR operator (||)

```bash
# Run alternative if command fails
cd /opt/app || { echo "ERROR: directory not found"; exit 1; }

# With a function
die() { echo "FATAL: $1" >&2; exit "${2:-1}"; }

cd /opt/app || die "Cannot find /opt/app"
git pull || die "Git pull failed"
```

### Pattern 2: If statement check

```bash
# Explicit check
if ! docker build -t myapp .; then
  echo "Docker build failed!"
  exit 1
fi

# Check exit code directly
docker push myimage:latest
if [ $? -ne 0 ]; then
  echo "Push failed!"
  notify_team "Docker push failed"
  exit 1
fi
```

### Pattern 3: trap — Cleanup on exit/error

`trap` catches signals and runs code when they occur:

```bash
#!/bin/bash
set -euo pipefail

TEMP_DIR=$(mktemp -d)
LOCK_FILE="/tmp/deploy.lock"

# Cleanup function — runs no matter how script exits
cleanup() {
  echo "Cleaning up..."
  rm -rf "$TEMP_DIR"
  rm -f "$LOCK_FILE"
  echo "Cleanup done"
}

# Register the trap
trap cleanup EXIT       # Run cleanup on ANY exit (success or failure)

# Alternative traps:
# trap cleanup ERR     # Only on error
# trap cleanup SIGINT  # Only on Ctrl+C
# trap cleanup SIGTERM # Only on kill

# Now do work — cleanup runs automatically when script ends
touch "$LOCK_FILE"
echo "Working in $TEMP_DIR..."
cp files "$TEMP_DIR/"
# Even if something fails here, cleanup() still runs
process_files
```

### Pattern 4: Error handler function

```bash
#!/bin/bash
set -euo pipefail

# Called automatically on error (with trap ERR)
on_error() {
  local exit_code=$?
  local line_number=${BASH_LINENO[0]}
  local command="${BASH_COMMAND}"
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
  echo "ERROR on line $line_number" >&2
  echo "Command: $command" >&2
  echo "Exit code: $exit_code" >&2
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
}

trap on_error ERR

# Now any failed command shows detailed error info
echo "Starting..."
ls /nonexistent_path     # This will trigger on_error with line number!
echo "This won't run"
```

### Pattern 5: Retry with backoff

```bash
retry() {
  local max_attempts=${1}
  local delay=${2}
  shift 2
  local command="$@"
  
  local attempt=1
  while [ $attempt -le $max_attempts ]; do
    echo "  [$attempt/$max_attempts] $command"
    if eval "$command"; then
      return 0
    fi
    
    if [ $attempt -lt $max_attempts ]; then
      echo "  Retrying in ${delay}s..."
      sleep $delay
      delay=$((delay * 2))     # Exponential backoff
    fi
    attempt=$((attempt + 1))
  done
  
  echo "  FAILED after $max_attempts attempts" >&2
  return 1
}

# Usage
retry 3 5 curl -sf http://api.example.com/health
retry 5 2 docker push myapp:latest
```

---

## 🔍 Debugging Techniques

### Method 1: bash -x (trace execution)

The most powerful debugging tool. Shows EVERY command before it executes:

```bash
# Run script with tracing
bash -x script.sh

# Output looks like:
# + set -euo pipefail
# + APP_NAME=myapp
# + echo 'Starting deployment of myapp'
# Starting deployment of myapp
# + cd /opt/myapp
# + git pull origin main
```

### Method 2: set -x inside script (selective debugging)

```bash
#!/bin/bash

echo "Normal output (not traced)"

set -x    # ──── Tracing ON ────
# Everything below is traced
deploy_command
another_command
set +x    # ──── Tracing OFF ────

echo "Normal output again"
```

### Method 3: Debug function

```bash
DEBUG=${DEBUG:-false}    # Set DEBUG=true to enable

debug() {
  if [ "$DEBUG" = true ]; then
    echo "[DEBUG] $@" >&2
  fi
}

debug "Variable x = $x"
debug "About to call API"
debug "Response code: $status"

# Run with debugging:
# DEBUG=true ./script.sh
```

### Method 4: Syntax check without running

```bash
bash -n script.sh              # Check syntax only (no execution)
# No output = no syntax errors
# Shows error location if there's a problem
```

### Method 5: ShellCheck (static analysis)

```bash
# Install
apt install shellcheck

# Run against your script
shellcheck script.sh

# Output:
# In script.sh line 10:
#   echo $name
#        ^-- SC2086: Double quote to prevent globbing and word splitting.
```

### Method 6: Print variable state at key points

```bash
#!/bin/bash

echo "=== DEBUG INFO ===" >&2
echo "Script: $0" >&2
echo "Args: $@" >&2
echo "PWD: $PWD" >&2
echo "USER: $USER" >&2
echo "==================" >&2

# Or use a function
dump_vars() {
  echo "--- State at line ${BASH_LINENO[0]} ---" >&2
  echo "  server=$server" >&2
  echo "  version=$version" >&2
  echo "  status=$status" >&2
  echo "---" >&2
}
```

---

## 🛠️ Complete Production Error Handling Template

```bash
#!/bin/bash
set -euo pipefail

# ── Configuration ──
readonly SCRIPT_NAME=$(basename "$0")
readonly LOG_FILE="/var/log/${SCRIPT_NAME%.sh}.log"

# ── Logging ──
log()   { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$1] $2" | tee -a "$LOG_FILE"; }
info()  { log "INFO" "$1"; }
warn()  { log "WARN" "$1"; }
error() { log "ERROR" "$1" >&2; }
die()   { error "$1"; exit "${2:-1}"; }

# ── Error trap ──
on_error() {
  error "Failed at line ${BASH_LINENO[0]}: ${BASH_COMMAND} (exit code: $?)"
  # Send alert
  # curl -X POST slack_webhook -d '{"text":"Script failed!"}'
}
trap on_error ERR

# ── Cleanup trap ──
cleanup() {
  info "Cleaning up temporary files..."
  rm -rf "${TEMP_DIR:-/tmp/nonexistent}"
}
trap cleanup EXIT

# ── Main ──
main() {
  info "Starting ${SCRIPT_NAME}"
  
  # Validate prerequisites
  [ -f "config.yml" ] || die "config.yml not found"
  command -v docker &>/dev/null || die "docker not installed"
  
  # Do work
  info "Building application..."
  docker build -t myapp . || die "Build failed"
  
  info "Running tests..."
  docker run --rm myapp pytest || die "Tests failed"
  
  info "Pushing image..."
  docker push myapp:latest || die "Push failed"
  
  info "✓ ${SCRIPT_NAME} completed successfully"
}

main "$@"
```

---

## 🎯 Interview Quick Points

- `set -euo pipefail` = strict mode (use in ALL production scripts)
- `set -e` exits on any error
- `set -u` errors on undefined variables
- `set -o pipefail` catches pipe failures
- `trap cleanup EXIT` ensures cleanup always runs
- `trap on_error ERR` catches errors with context (line number, command)
- `bash -x script.sh` traces every command for debugging
- `bash -n script.sh` checks syntax without running
- `|| die "message"` is a clean error pattern
- `$?` holds last command's exit code
- `${BASH_LINENO[0]}` gives error line number in trap
- `${BASH_COMMAND}` gives the command that failed
- `shellcheck` is a static analysis tool for bash
- Always send error messages to stderr: `>&2`
