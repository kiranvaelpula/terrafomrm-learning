# Variables and Data Types

> **Variables in bash store data as strings by default. Understanding variable types, scope, and special variables is essential for effective scripting.**

---

## 📖 What are Variables?

Variables are **named containers** that hold data. In bash, everything is stored as a **string** — there are no strict data types like in Python or Java.

```bash
# Think of it as a labeled box:
#   ┌────────────┐
#   │  "DevOps"  │  ← Value stored inside
#   └────────────┘
#       name        ← Variable name (label on the box)
```

---

## 🎯 Declaring Variables

### Rules for Variable Names:
- Can contain: letters, numbers, underscore
- Must START with: letter or underscore (not a number)
- Case SENSITIVE: `Name` and `name` are different variables
- NO SPACES around `=` sign

```bash
# ✅ Correct
name="Kiran"
age=25
_private="secret"
MY_CONSTANT="fixed"
server_ip="10.0.1.50"

# ❌ Wrong
name = "Kiran"      # Error! Shell thinks "name" is a command
2name="bad"         # Error! Cannot start with number
my-var="bad"        # Error! Hyphens not allowed (interpreted as minus)
```

---

## 📋 Using Variables

```bash
name="DevOps"
version=3

# Method 1: Dollar sign
echo $name                    # Output: DevOps

# Method 2: Curly braces (RECOMMENDED)
echo ${name}                  # Output: DevOps
echo "${name}_engineer"       # Output: DevOps_engineer
# Without braces: echo "$name_engineer" → empty (looks for $name_engineer)

# Method 3: Inside double quotes (variables expand)
echo "Welcome to $name v${version}"    # Output: Welcome to DevOps v3

# Single quotes: NO expansion (literal string)
echo 'Welcome to $name'               # Output: Welcome to $name (literal)
```

**Key Rule:** Always use `"${variable}"` with double quotes and braces for safety.

---

## 🏷️ Types of Variables

### 1. User-Defined Variables (you create them)

```bash
app_name="my-web-app"
port=8080
log_dir="/var/log/myapp"
is_production=true
deploy_date="2026-08-10"
```

### 2. Environment Variables (system-wide, inherited by child processes)

```bash
# View all environment variables
env
printenv

# Common environment variables
echo $HOME            # /home/username — user's home directory
echo $USER            # username — current logged in user
echo $PATH            # /usr/local/bin:/usr/bin — where shell looks for commands
echo $SHELL           # /bin/bash — current shell
echo $PWD             # /opt/app — current working directory
echo $HOSTNAME        # server-01 — machine name
echo $TERM            # xterm-256color — terminal type
echo $LANG            # en_US.UTF-8 — language setting
echo $EDITOR          # vim — default text editor

# Create environment variable (available to child processes)
export DB_HOST="localhost"
export DB_PORT=5432
export APP_ENV="production"

# Check if variable is exported
export -p | grep DB_HOST
```

**Difference between regular and environment variables:**
```bash
# Regular variable — only in current shell
greeting="hello"
bash -c 'echo $greeting'       # Output: (empty — child can't see it)

# Environment variable — inherited by children
export greeting="hello"
bash -c 'echo $greeting'       # Output: hello
```

### 3. Special Variables (built-in by bash)

```bash
$0     # Name of the script itself
$1     # First argument passed to script
$2     # Second argument
$3     # Third argument... up to $9 (${10} for 10+)
$#     # Total NUMBER of arguments
$@     # ALL arguments as separate words ("$1" "$2" "$3")
$*     # ALL arguments as single string ("$1 $2 $3")
$$     # PID (Process ID) of the current script
$?     # Exit code of the LAST command (0=success)
$!     # PID of the last background process
$_     # Last argument of the previous command
```

**Example showing special variables:**
```bash
#!/bin/bash
# Save as: deploy.sh
# Run as:  ./deploy.sh staging v2.0.1 --force

echo "Script name:       $0"       # ./deploy.sh
echo "First argument:    $1"       # staging
echo "Second argument:   $2"       # v2.0.1
echo "Third argument:    $3"       # --force
echo "Total arguments:   $#"       # 3
echo "All arguments:     $@"       # staging v2.0.1 --force
echo "Script PID:        $$"       # 12345 (some number)
```

### 4. Readonly Variables (constants)

```bash
readonly PI=3.14159
readonly MAX_RETRIES=5
readonly CONFIG_FILE="/etc/app/config.yml"

PI=3.14            # Error: PI: readonly variable
```

---

## 🔢 Arithmetic Operations

Bash variables are strings, so you need special syntax for math:

```bash
# Method 1: $(( )) — RECOMMENDED
result=$((5 + 3))
echo $result    # 8

a=10
b=3
echo $((a + b))     # 13  Addition
echo $((a - b))     # 7   Subtraction
echo $((a * b))     # 30  Multiplication
echo $((a / b))     # 3   Division (integer only! no decimals)
echo $((a % b))     # 1   Modulo (remainder)
echo $((2 ** 10))   # 1024  Power/exponent

# Increment/Decrement
count=0
count=$((count + 1))     # Now count=1
((count++))              # Now count=2
((count--))              # Back to count=1

# Method 2: let
let "sum = 10 + 20"
let "product = 5 * 4"

# Method 3: expr (older, requires spaces)
result=$(expr 5 + 3)     # 8
result=$(expr 5 \* 3)    # 15 (must escape *)

# For decimal/floating point — use bc
echo "10 / 3" | bc -l         # 3.33333333333
echo "scale=2; 10/3" | bc     # 3.33
```

---

## 📝 String Operations

Bash has powerful built-in string manipulation:

```bash
str="Hello World of DevOps"

# Length of string
echo ${#str}                    # 21

# Substring extraction: ${var:offset:length}
echo ${str:0:5}                 # Hello (start at 0, take 5 chars)
echo ${str:6:5}                 # World (start at 6, take 5 chars)
echo ${str:6}                   # World of DevOps (from offset to end)
echo ${str: -6}                 # DevOps (last 6 chars — note the space before -)

# Replace first occurrence: ${var/pattern/replacement}
echo ${str/World/Bash}          # Hello Bash of DevOps

# Replace ALL occurrences: ${var//pattern/replacement}
text="one-two-one-three"
echo ${text//one/1}             # 1-two-1-three

# Remove prefix: ${var#pattern}
filepath="/var/log/app/server.log"
echo ${filepath#*/}             # var/log/app/server.log (remove shortest prefix match)
echo ${filepath##*/}            # server.log (remove longest prefix match — basename)

# Remove suffix: ${var%pattern}
echo ${filepath%/*}             # /var/log/app (remove shortest suffix — dirname)
echo ${filepath%%/*}            # (empty — remove longest suffix)

# Case conversion (bash 4+)
name="hello world"
echo ${name^}                   # Hello world (capitalize first letter)
echo ${name^^}                  # HELLO WORLD (all uppercase)

name="HELLO WORLD"
echo ${name,}                   # hELLO WORLD (lowercase first letter)
echo ${name,,}                  # hello world (all lowercase)

# Default values (very useful!)
echo ${DB_HOST:-"localhost"}    # Use "localhost" if DB_HOST is empty/unset
echo ${DB_PORT:=5432}           # SET DB_PORT to 5432 if empty/unset
echo ${APP_NAME:?"Error: APP_NAME must be set"}   # Exit with error if unset
```

---

## 📋 Arrays

```bash
# Create an indexed array
fruits=("apple" "banana" "cherry" "date" "elderberry")
servers=("web01" "web02" "db01" "cache01")

# Access elements (0-indexed)
echo ${fruits[0]}              # apple
echo ${fruits[2]}              # cherry
echo ${fruits[-1]}             # elderberry (last element)

# All elements
echo ${fruits[@]}              # apple banana cherry date elderberry
echo "${fruits[@]}"            # Each element as separate word (ALWAYS quote!)

# Array length
echo ${#fruits[@]}             # 5

# Add element
fruits+=("fig")
fruits+=("grape" "honeydew")   # Add multiple

# Remove element (leaves gap in index)
unset fruits[1]                # Removes "banana"

# Slice: ${array[@]:offset:count}
echo ${fruits[@]:1:3}          # banana cherry date (3 elements starting from index 1)

# Loop through array
for fruit in "${fruits[@]}"; do     # ALWAYS quote "${arr[@]}"
  echo "I like $fruit"
done

# Loop with index
for i in "${!fruits[@]}"; do        # ${!arr[@]} gives indices
  echo "Index $i: ${fruits[$i]}"
done

# Associative arrays (key-value, like dictionaries — bash 4+)
declare -A config
config[host]="10.0.1.50"
config[port]="8080"
config[env]="production"

echo ${config[host]}           # 10.0.1.50
echo ${!config[@]}             # host port env (all keys)
echo ${config[@]}              # all values
```

---

## 💡 Command Substitution

Capture the output of a command into a variable:

```bash
# Modern syntax: $(command)
current_date=$(date)
file_count=$(ls /var/log | wc -l)
ip_address=$(hostname -I | awk '{print $1}')
git_branch=$(git rev-parse --abbrev-ref HEAD)
free_memory=$(free -m | awk '/Mem/{print $4}')

echo "Date: $current_date"
echo "Log files: $file_count"
echo "IP: $ip_address"
echo "Branch: $git_branch"
echo "Free RAM: ${free_memory}MB"

# Old syntax: `command` (backticks — harder to read, avoid)
old_way=`date`
```

---

## 🔍 Variable Scope

```bash
# GLOBAL (default — any variable you set is global)
global_var="I'm everywhere"

my_function() {
  # LOCAL — only exists inside this function
  local local_var="I'm only here"
  
  # Can access global variables
  echo $global_var          # Works: I'm everywhere
  
  # Modifying global inside function affects it outside
  global_var="Modified!"
}

my_function
echo $global_var       # Output: Modified!
echo $local_var        # Output: (empty — doesn't exist here)
```

**Best practice:** Always use `local` inside functions to avoid accidentally changing global state.

---

## 🛠️ Practical Examples

### Reading user input

```bash
# Simple input
echo "Enter your name:"
read name
echo "Hello, $name!"

# Prompt on same line
read -p "Enter environment (dev/prod): " env

# Silent input (for passwords)
read -sp "Enter password: " password
echo ""    # New line after silent input

# With timeout
read -t 5 -p "Confirm? (y/n): " answer   # 5 second timeout
```

### Using variables in DevOps scripts

```bash
#!/bin/bash
# Deployment script using variables

# Configuration
APP_NAME="my-webapp"
DEPLOY_DIR="/opt/${APP_NAME}"
BACKUP_DIR="/backups/${APP_NAME}"
LOG_FILE="/var/log/${APP_NAME}/deploy.log"
VERSION="${1:?Error: Version argument required}"    # Exit if not provided
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Use them
echo "Deploying ${APP_NAME} v${VERSION} to ${DEPLOY_DIR}"
echo "Backup location: ${BACKUP_DIR}/${TIMESTAMP}"
echo "Logging to: ${LOG_FILE}"
```

---

## 🎯 Interview Quick Points

- Variables are untyped (everything is a string by default)
- NO SPACES around `=` when assigning: `var="value"`
- Use `${}` with braces for variable expansion (clearer, safer)
- `export` makes a variable available to child processes
- `local` limits scope to the current function
- `$?` = last command's exit status (0=success)
- `$@` = all script arguments (as separate words)
- `$#` = number of arguments
- `readonly` makes a variable immutable (constant)
- Use `$(command)` for command substitution
- Always QUOTE your variables: `"$var"` to handle spaces safely
- `${var:-default}` provides a fallback value if var is empty
