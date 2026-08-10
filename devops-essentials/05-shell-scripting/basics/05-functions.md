# Functions in Shell Scripting

> **Functions group reusable code blocks that can be called multiple times, making scripts modular, readable, and maintainable.**

---

## 📖 Why Functions?

Without functions:
```bash
# Copy-paste the same 10 lines every time you need them
echo "[$(date)] Starting deploy to web01..."
scp app.tar.gz user@web01:/opt/
ssh user@web01 "tar -xzf /opt/app.tar.gz && systemctl restart app"
echo "[$(date)] Deploy to web01 complete"

echo "[$(date)] Starting deploy to web02..."  # Same code repeated!
scp app.tar.gz user@web02:/opt/
ssh user@web02 "tar -xzf /opt/app.tar.gz && systemctl restart app"
echo "[$(date)] Deploy to web02 complete"
```

With functions:
```bash
deploy_to() {
  local server=$1
  echo "[$(date)] Starting deploy to $server..."
  scp app.tar.gz user@$server:/opt/
  ssh user@$server "tar -xzf /opt/app.tar.gz && systemctl restart app"
  echo "[$(date)] Deploy to $server complete"
}

deploy_to "web01"
deploy_to "web02"
deploy_to "web03"
```

Functions make code: **reusable**, **readable**, **testable**, and **maintainable**.

---

## 🎯 Declaring and Calling Functions

### Two Syntax Options

```bash
# Method 1: Simple (PREFERRED)
function_name() {
  commands
}

# Method 2: With 'function' keyword
function function_name {
  commands
}
```

### Calling Functions

```bash
greet() {
  echo "Hello, World!"
}

# Call by name — no parentheses!
greet
greet        # Can call multiple times
```

**Important Rules:**
- Functions must be DEFINED BEFORE they are called
- No parentheses when calling: `greet` not `greet()`
- Function names follow same rules as variables (letters, numbers, underscores)

---

## 📥 Functions with Arguments

Functions receive arguments through positional parameters (`$1`, `$2`, etc.) — just like scripts receive command-line arguments:

```bash
greet_user() {
  local name=$1           # First argument
  local role=$2           # Second argument
  
  echo "Hello, $name!"
  echo "Your role is: $role"
  echo "You passed $# arguments"   # Number of args to THIS function
}

# Call with arguments (separated by space)
greet_user "Kiran" "DevOps Engineer"
greet_user "John" "Developer"
```

**Inside a function, $1, $2, etc. refer to the FUNCTION'S arguments, NOT the script's arguments.**

### Handling variable number of arguments

```bash
# $@ gives all arguments as separate words
install_packages() {
  echo "Installing ${#} packages..."    # $# = count
  for package in "$@"; do               # $@ = all args
    echo "  Installing: $package"
    apt install -y "$package" 2>/dev/null
  done
}

install_packages "nginx" "curl" "git" "vim"
```

---

## 🔄 Return Values

Bash functions can "return" data in two ways:

### Method 1: `echo` — Return strings/data (MOST COMMON)

```bash
get_timestamp() {
  echo $(date +%Y-%m-%d_%H:%M:%S)    # "Return" by printing
}

# Capture output with command substitution
ts=$(get_timestamp)
echo "Timestamp: $ts"    # Timestamp: 2026-08-10_14:30:00

get_ip() {
  echo $(hostname -I | awk '{print $1}')
}

my_ip=$(get_ip)
echo "My IP: $my_ip"
```

### Method 2: `return` — Return exit codes only (0-255)

`return` is like `exit` but for functions. It sets the exit status, not a string value.

```bash
is_root() {
  if [ "$(id -u)" -eq 0 ]; then
    return 0     # 0 = success = true
  else
    return 1     # non-zero = failure = false
  fi
}

# Use in if condition (checks return code)
if is_root; then
  echo "Running as root ✓"
else
  echo "Not root! Please use sudo."
  exit 1
fi

# Check service health
is_healthy() {
  local url=$1
  curl -sf "$url" > /dev/null
  return $?        # Return curl's exit code
}

if is_healthy "http://localhost:8080/health"; then
  echo "Service is healthy"
fi
```

**Key difference:**
- `echo` → returns DATA (strings, numbers, any text)
- `return` → returns STATUS (0=success, 1-255=failure)

---

## 🔍 Variable Scope (local vs global)

**By default, all variables in bash are GLOBAL:**

```bash
name="Original"

change_name() {
  name="Modified"       # Changes the GLOBAL variable!
}

echo $name      # Original
change_name
echo $name      # Modified ← Oops! Function changed our variable
```

**Use `local` to keep variables inside the function:**

```bash
counter=100

my_function() {
  local counter=0       # This is a DIFFERENT variable (local)
  local temp="working"
  counter=$((counter + 1))
  echo "Inside: counter=$counter"     # Inside: counter=1
}

my_function
echo "Outside: counter=$counter"      # Outside: counter=100 ← Unchanged!
echo "Outside: temp=$temp"            # Outside: temp= ← Empty (local died)
```

**Best Practice:** ALWAYS use `local` for function variables unless you intentionally want to modify global state.

```bash
deploy() {
  local server=$1
  local version=$2
  local status=""
  local log_file="/tmp/deploy_${server}.log"
  
  # All these variables die when the function ends
  # The calling code's variables are safe
}
```

---

## 🛠️ Practical Function Examples

### Logging functions

```bash
# Colored logging
log_info()  { echo -e "\033[32m[INFO]\033[0m  $(date '+%H:%M:%S') $1"; }
log_warn()  { echo -e "\033[33m[WARN]\033[0m  $(date '+%H:%M:%S') $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $(date '+%H:%M:%S') $1" >&2; }

log_info "Starting deployment"
log_warn "Using default config"
log_error "Connection refused"
```

### Die function (exit with error message)

```bash
die() {
  local message=$1
  local code=${2:-1}     # Default exit code is 1 if not provided
  
  echo "FATAL: $message" >&2    # Print to stderr
  exit $code
}

# Usage
[ -f "config.yml" ] || die "Config file not found"
[ -n "$DB_HOST" ]   || die "DB_HOST environment variable not set"
```

### Retry wrapper

```bash
retry() {
  local max_attempts=$1
  local delay=$2
  shift 2                   # Remove first 2 args, leaving the command
  local command="$@"
  
  local attempt=1
  while [ $attempt -le $max_attempts ]; do
    echo "  Attempt $attempt/$max_attempts: $command"
    if eval "$command"; then
      return 0
    fi
    echo "  Failed. Waiting ${delay}s..."
    sleep $delay
    attempt=$((attempt + 1))
  done
  
  echo "  All $max_attempts attempts failed!"
  return 1
}

# Usage
retry 3 5 curl -sf http://api.example.com/health
retry 5 10 docker pull myimage:latest
```

### Check if command exists

```bash
require_cmd() {
  local cmd=$1
  if ! command -v "$cmd" &> /dev/null; then
    die "'$cmd' is required but not installed"
  fi
}

require_cmd "docker"
require_cmd "kubectl"
require_cmd "helm"
echo "All required tools available ✓"
```

---

## 📚 Function Libraries (Sourcing)

Put reusable functions in a separate file and `source` them:

```bash
# lib/common.sh — Reusable function library
#!/bin/bash

log_info()  { echo "[INFO]  $(date '+%H:%M:%S') $1"; }
log_error() { echo "[ERROR] $(date '+%H:%M:%S') $1" >&2; }
die()       { log_error "$1"; exit "${2:-1}"; }

require_root() {
  [ "$(id -u)" -eq 0 ] || die "Must run as root"
}

require_cmd() {
  command -v "$1" >/dev/null || die "Command not found: $1"
}

check_health() {
  local url=$1
  local timeout=${2:-5}
  curl -sf --max-time $timeout "$url" > /dev/null
}
```

```bash
# deploy.sh — Main script sources the library
#!/bin/bash
source "$(dirname "$0")/lib/common.sh"    # Load functions

require_root
require_cmd "docker"

log_info "Starting deployment..."
if check_health "http://localhost:8080/health"; then
  log_info "App is running, performing rolling update..."
else
  log_error "App is down!"
fi
```

---

## 🎯 Interview Quick Points

- Functions MUST be defined before they are called
- Arguments: `$1`, `$2`, `$#` (count), `$@` (all)
- Use `local` for ALL variables inside functions
- `return` = exit code (0-255), NOT data
- `echo` inside function + `$(func)` to capture data
- `source file.sh` or `. file.sh` loads functions from external files
- Functions make scripts modular, testable, and reusable
- Common patterns: `die()`, `log_info()`, `retry()`, `require_cmd()`
- Functions are called without parentheses: `my_func arg1 arg2`
