# Conditionals and Operators

> **Conditional statements control the flow of your script based on conditions — if something is true, do this; otherwise, do that.**

---

## 📖 Why Conditionals?

Without conditionals, a script runs every line no matter what. With conditionals, you can:
- Check if a file exists before reading it
- Verify a service is running before deploying
- Handle different environments (dev vs prod)
- Respond to errors gracefully

---

## 🎯 If-Else Statements

### Basic Syntax

```bash
if [ condition ]; then
  # commands if condition is TRUE
fi

# With else
if [ condition ]; then
  # commands if TRUE
else
  # commands if FALSE
fi

# With elif (else if)
if [ condition1 ]; then
  # if condition1 is true
elif [ condition2 ]; then
  # if condition2 is true
else
  # if nothing matched
fi
```

**Important:** Spaces inside `[ ]` are REQUIRED!
```bash
if [ $age -gt 18 ]; then    # ✅ Correct (spaces after [ and before ])
if [$age -gt 18]; then      # ❌ Error! No spaces
```

### Real Example

```bash
#!/bin/bash

echo "Enter your age:"
read age

if [ $age -ge 18 ]; then
  echo "You are an adult"
  echo "You can vote"
elif [ $age -ge 13 ]; then
  echo "You are a teenager"
else
  echo "You are a child"
fi
```

---

## 🔢 Numeric Comparison Operators

Used to compare numbers inside `[ ]`:

```bash
-eq    # Equal to           ( == in math)
-ne    # Not equal to       ( != in math)
-gt    # Greater than       ( >  in math)
-ge    # Greater than or equal ( >= in math)
-lt    # Less than          ( <  in math)
-le    # Less than or equal ( <= in math)
```

**Examples:**
```bash
a=10
b=20

if [ $a -eq $b ]; then echo "Equal"; fi
if [ $a -ne $b ]; then echo "Not equal"; fi         # ✓ Prints
if [ $a -gt $b ]; then echo "a is greater"; fi
if [ $a -lt $b ]; then echo "a is less"; fi          # ✓ Prints
if [ $a -ge 10 ]; then echo "a is >= 10"; fi         # ✓ Prints
if [ $a -le 5 ]; then echo "a is <= 5"; fi

# DevOps example: Check disk usage
disk_usage=85
if [ $disk_usage -gt 80 ]; then
  echo "WARNING: Disk usage is ${disk_usage}%"
  echo "Sending alert..."
fi
```

---

## 📝 String Comparison Operators

```bash
=      # Equal (inside [ ])
==     # Equal (inside [[ ]] — preferred)
!=     # Not equal
-z     # String is EMPTY (zero length)
-n     # String is NOT empty
<      # Less than (alphabetical) — must use inside [[ ]]
>      # Greater than (alphabetical) — must use inside [[ ]]
```

**Examples:**
```bash
name="admin"
env=""

# String equality
if [ "$name" = "admin" ]; then
  echo "Welcome, administrator!"
fi

# Check if empty
if [ -z "$env" ]; then
  echo "ERROR: Environment variable is empty"
  exit 1
fi

# Check if not empty
if [ -n "$name" ]; then
  echo "Name is set to: $name"
fi

# DevOps example: Validate environment
ENVIRONMENT="$1"
if [ -z "$ENVIRONMENT" ]; then
  echo "Usage: $0 <environment>"
  echo "Environments: dev, staging, production"
  exit 1
fi

if [ "$ENVIRONMENT" != "dev" ] && [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
  echo "ERROR: Invalid environment '$ENVIRONMENT'"
  exit 1
fi
```

**ALWAYS quote string variables in comparisons:**
```bash
name=""
if [ $name = "admin" ]; then    # ❌ Error! Becomes [ = "admin" ] — broken
if [ "$name" = "admin" ]; then  # ✅ Correct! Becomes [ "" = "admin" ] — works
```

---

## 📂 File Test Operators

Check properties of files and directories:

```bash
-f file    # TRUE if file EXISTS and is a regular FILE
-d file    # TRUE if file EXISTS and is a DIRECTORY
-e file    # TRUE if file EXISTS (file or directory)
-r file    # TRUE if file is READABLE
-w file    # TRUE if file is WRITABLE
-x file    # TRUE if file is EXECUTABLE
-s file    # TRUE if file is NOT EMPTY (size > 0)
-L file    # TRUE if file is a SYMBOLIC LINK
-O file    # TRUE if you OWN the file

# For comparing files:
file1 -nt file2    # file1 is NEWER than file2
file1 -ot file2    # file1 is OLDER than file2
```

**Examples:**
```bash
# Check if config file exists
config="/etc/app/config.yml"
if [ -f "$config" ]; then
  echo "Loading config from $config"
  source "$config"
else
  echo "ERROR: Config file not found: $config"
  exit 1
fi

# Check if directory exists, create if not
log_dir="/var/log/myapp"
if [ ! -d "$log_dir" ]; then      # ! = NOT
  echo "Creating log directory: $log_dir"
  mkdir -p "$log_dir"
fi

# Check if script has execute permission
if [ ! -x "/opt/app/deploy.sh" ]; then
  echo "Making deploy script executable..."
  chmod +x /opt/app/deploy.sh
fi

# Check if log file has content
if [ -s "/var/log/errors.log" ]; then
  echo "There are errors to review!"
  tail -20 /var/log/errors.log
else
  echo "No errors. All good!"
fi
```

---

## 🔗 Logical Operators

Combine multiple conditions:

```bash
# AND — both conditions must be true
# Method 1: separate [ ] with &&
if [ $age -gt 18 ] && [ $age -lt 65 ]; then
  echo "Working age"
fi

# Method 2: inside [[ ]]
if [[ $age -gt 18 && $age -lt 65 ]]; then
  echo "Working age"
fi

# OR — at least one condition must be true
if [ "$env" = "dev" ] || [ "$env" = "staging" ]; then
  echo "Non-production environment"
fi

if [[ "$env" = "dev" || "$env" = "staging" ]]; then
  echo "Non-production environment"
fi

# NOT — inverts the condition
if [ ! -f "lockfile" ]; then
  echo "No lock file — safe to proceed"
fi

if ! systemctl is-active --quiet nginx; then
  echo "Nginx is NOT running!"
fi
```

**DevOps example: Pre-deployment checks**
```bash
#!/bin/bash
# Check all conditions before deploying

errors=0

if [ ! -f "docker-compose.yml" ]; then
  echo "✗ docker-compose.yml not found"
  errors=$((errors + 1))
fi

if ! command -v docker &> /dev/null; then
  echo "✗ Docker is not installed"
  errors=$((errors + 1))
fi

if [ ! -r ".env" ]; then
  echo "✗ .env file not readable"
  errors=$((errors + 1))
fi

if [ $errors -gt 0 ]; then
  echo "Deployment aborted: $errors pre-check(s) failed"
  exit 1
fi

echo "✓ All pre-checks passed. Deploying..."
```

---

## 🔄 Case Statement (Switch)

When you have many conditions to check against one value, `case` is cleaner than multiple `if-elif`:

```bash
#!/bin/bash
# case syntax:
case $variable in
  pattern1)
    commands
    ;;                    # ;; marks end of this case
  pattern2)
    commands
    ;;
  pattern3|pattern4)      # Multiple patterns with |
    commands
    ;;
  *)                      # Default (like else)
    commands
    ;;
esac                      # "case" spelled backwards = end
```

**Real examples:**
```bash
#!/bin/bash
# Service management script

action="$1"
service="$2"

case $action in
  start)
    echo "Starting $service..."
    systemctl start $service
    ;;
  stop)
    echo "Stopping $service..."
    systemctl stop $service
    ;;
  restart)
    echo "Restarting $service..."
    systemctl restart $service
    ;;
  status)
    systemctl status $service
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status} <service_name>"
    exit 1
    ;;
esac
```

```bash
#!/bin/bash
# Environment-specific configuration

case "$ENVIRONMENT" in
  dev|development)
    DB_HOST="dev-db.internal"
    REPLICAS=1
    DEBUG=true
    ;;
  staging|stg)
    DB_HOST="staging-db.internal"
    REPLICAS=2
    DEBUG=false
    ;;
  prod|production)
    DB_HOST="prod-db.internal"
    REPLICAS=5
    DEBUG=false
    ;;
  *)
    echo "Unknown environment: $ENVIRONMENT"
    exit 1
    ;;
esac

echo "DB_HOST=$DB_HOST, REPLICAS=$REPLICAS, DEBUG=$DEBUG"
```

---

## 🔲 [ ] vs [[ ]] — Which to Use?

| Feature | `[ ]` (test command) | `[[ ]]` (bash keyword) |
|---------|---------------------|------------------------|
| POSIX compatible | ✅ Works in sh, dash, etc. | ❌ Bash only |
| Word splitting | YES (must quote vars!) | NO (safer) |
| Pattern matching | ❌ | ✅ `[[ $str == h* ]]` |
| Regex matching | ❌ | ✅ `[[ $str =~ regex ]]` |
| Logical AND/OR | `-a` / `-o` (inside) | `&&` / `||` (inside) |
| Empty variable | Can cause errors | Handles safely |

```bash
# Pattern matching (only in [[ ]])
filename="deploy-2026-08-10.log"
if [[ "$filename" == deploy-* ]]; then
  echo "This is a deployment log"
fi

if [[ "$filename" == *.log ]]; then
  echo "This is a log file"
fi

# Regex matching (only in [[ ]])
email="user@example.com"
if [[ "$email" =~ ^[a-zA-Z0-9.]+@[a-zA-Z]+\.[a-zA-Z]+$ ]]; then
  echo "Valid email format"
else
  echo "Invalid email format"
fi

# Check if string is a number
value="12345"
if [[ "$value" =~ ^[0-9]+$ ]]; then
  echo "$value is a number"
fi
```

**Recommendation:** Use `[[ ]]` for bash scripts. Use `[ ]` only if you need POSIX compatibility (scripts that must work on minimal systems).

---

## 💡 Ternary-like Expressions

Bash doesn't have a `?:` ternary operator, but you can simulate it:

```bash
# Method 1: && and ||
age=20
status=$([ $age -ge 18 ] && echo "Adult" || echo "Minor")
echo $status    # Adult

# Method 2: Inline if
[[ $DEBUG == true ]] && echo "Debug mode ON" || echo "Debug mode OFF"

# Method 3: One-liner if
if [ -f "app.pid" ]; then echo "Running"; else echo "Stopped"; fi
```

---

## 🛠️ Practical DevOps Examples

### Check if running as root
```bash
if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root (use sudo)"
  exit 1
fi
```

### Validate required commands exist
```bash
for cmd in docker kubectl helm; do
  if ! command -v $cmd &> /dev/null; then
    echo "ERROR: '$cmd' is required but not installed"
    exit 1
  fi
done
echo "All required tools are available"
```

### Handle different OS types
```bash
OS=$(uname -s)
case $OS in
  Linux)
    PACKAGE_MGR="apt"
    ;;
  Darwin)
    PACKAGE_MGR="brew"
    ;;
  *)
    echo "Unsupported OS: $OS"
    exit 1
    ;;
esac
echo "Using package manager: $PACKAGE_MGR"
```

---

## 🎯 Interview Quick Points

- `[ ]` is POSIX-compatible, `[[ ]]` is bash-specific (more powerful)
- Always QUOTE variables in conditions: `"$var"`
- Numeric comparisons: `-eq`, `-ne`, `-gt`, `-lt`, `-ge`, `-le`
- String comparisons: `=`, `!=`, `-z` (empty), `-n` (not empty)
- File tests: `-f` (file), `-d` (directory), `-e` (exists), `-r` (readable), `-x` (executable)
- `case` is cleaner than multiple `if-elif` for matching one value
- `&&` = AND, `||` = OR, `!` = NOT
- `[[ ]]` supports pattern matching (`*`) and regex (`=~`)
- Spaces inside brackets are mandatory: `[ $a -eq $b ]`
