# Loops in Shell Scripting

> **Loops execute a block of code repeatedly — essential for processing files, iterating lists, and automating repetitive tasks.**

---

## 📖 Why Loops?

Without loops, if you need to deploy to 10 servers:
```bash
# Without loops (terrible)
ssh user@server1 "deploy.sh"
ssh user@server2 "deploy.sh"
ssh user@server3 "deploy.sh"
# ... 7 more lines
```

With loops:
```bash
# With loops (clean)
for server in server{1..10}; do
  ssh user@$server "deploy.sh"
done
```

---

## 🔁 For Loop

Iterates over a list of items.

### Basic Syntax

```bash
for variable in list_of_items; do
  commands
done
```

### Examples — Different Ways to Create Lists

```bash
# 1. Explicit list
for color in red green blue; do
  echo "Color: $color"
done

# 2. Range with braces
for i in {1..5}; do
  echo "Number: $i"         # 1, 2, 3, 4, 5
done

# 3. Range with step
for i in {0..20..5}; do
  echo $i                   # 0, 5, 10, 15, 20
done

# 4. Command output
for user in $(cat /etc/passwd | cut -d: -f1); do
  echo "User: $user"
done

# 5. Files using glob pattern
for file in /var/log/*.log; do
  echo "Log file: $file ($(wc -l < "$file") lines)"
done

# 6. Array elements
servers=("web01" "web02" "web03" "db01")
for server in "${servers[@]}"; do
  echo "Checking $server..."
done
```

### C-Style For Loop (when you need a counter)

```bash
# Syntax: for (( init; condition; increment ))
for (( i=1; i<=5; i++ )); do
  echo "Iteration: $i"
done

# Countdown
for (( i=10; i>=0; i-- )); do
  echo -n "$i "
done
echo "LAUNCH!"

# Use variable as limit
max=100
for (( i=0; i<max; i+=10 )); do
  echo "Progress: $i%"
done
```

### DevOps For Loop Examples

```bash
# Deploy to multiple servers
servers=("10.0.1.10" "10.0.1.11" "10.0.1.12")
for server in "${servers[@]}"; do
  echo "Deploying to $server..."
  scp app.tar.gz user@$server:/opt/
  ssh user@$server "cd /opt && tar -xzf app.tar.gz && systemctl restart app"
  if [ $? -eq 0 ]; then
    echo "  ✓ $server done"
  else
    echo "  ✗ $server FAILED"
  fi
done

# Check multiple services
services=("nginx" "docker" "postgresql" "redis")
for svc in "${services[@]}"; do
  if systemctl is-active --quiet $svc; then
    echo "  ✓ $svc is running"
  else
    echo "  ✗ $svc is STOPPED"
  fi
done

# Process multiple config files
for config in /etc/nginx/sites-enabled/*; do
  echo "Testing: $config"
  nginx -t -c "$config" 2>/dev/null
done
```

---

## 🔄 While Loop

Repeats AS LONG AS the condition is TRUE. Used when you don't know how many iterations you need.

### Basic Syntax

```bash
while [ condition ]; do
  commands
done
```

### Examples

```bash
# Simple counter
count=1
while [ $count -le 5 ]; do
  echo "Count: $count"
  count=$((count + 1))
done

# Read file line by line (SAFEST method)
while IFS= read -r line; do
  echo "Line: $line"
done < /etc/hosts
# IFS=   → preserves leading/trailing whitespace
# -r     → doesn't interpret backslashes

# Infinite loop (with break condition)
while true; do
  echo "Enter 'quit' to exit:"
  read input
  if [ "$input" = "quit" ]; then
    break         # Exit the loop
  fi
  echo "You typed: $input"
done
```

### DevOps While Loop Examples

```bash
# Wait for a service to be ready (with timeout)
echo "Waiting for application to start..."
max_wait=60
waited=0

while ! curl -sf http://localhost:8080/health > /dev/null; do
  if [ $waited -ge $max_wait ]; then
    echo "ERROR: Service did not start within ${max_wait}s"
    exit 1
  fi
  echo "  Still waiting... (${waited}s elapsed)"
  sleep 5
  waited=$((waited + 5))
done
echo "✓ Application is ready! (took ${waited}s)"

# Monitor disk usage continuously
while true; do
  usage=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
  timestamp=$(date '+%H:%M:%S')
  
  if [ $usage -gt 80 ]; then
    echo "[$timestamp] WARNING: Disk at ${usage}%"
  else
    echo "[$timestamp] OK: Disk at ${usage}%"
  fi
  
  sleep 60    # Check every minute
done

# Process queue items
while [ -f /tmp/queue/next_job ]; do
  job=$(cat /tmp/queue/next_job)
  echo "Processing: $job"
  process_job "$job"
  rm /tmp/queue/next_job
done

# Read from pipe
echo -e "web01\nweb02\nweb03" | while read server; do
  echo "Pinging $server..."
  ping -c 1 $server &>/dev/null && echo "  UP" || echo "  DOWN"
done
```

---

## ⏪ Until Loop

Opposite of `while` — loops UNTIL condition becomes TRUE (runs while condition is FALSE).

```bash
until [ condition ]; do
  commands
done
```

```bash
# Wait until file appears
echo "Waiting for deployment flag file..."
until [ -f /tmp/deploy_ready.flag ]; do
  echo "  Not ready yet..."
  sleep 2
done
echo "✓ Deployment flag detected! Proceeding..."

# Wait until port is available
until nc -z localhost 5432 2>/dev/null; do
  echo "Waiting for PostgreSQL on port 5432..."
  sleep 1
done
echo "PostgreSQL is accepting connections!"
```

---

## 🎛️ Loop Control Statements

### break — Exit the loop immediately

```bash
# Stop when you find what you're looking for
for server in web01 web02 web03 db01 db02; do
  if [[ $server == db* ]]; then
    echo "Found first database server: $server"
    break       # Stop looping
  fi
  echo "Skipping web server: $server"
done
# Output:
# Skipping web server: web01
# Skipping web server: web02
# Skipping web server: web03
# Found first database server: db01
```

### continue — Skip rest of current iteration, go to next

```bash
# Process only .log files, skip everything else
for file in /var/log/*; do
  if [[ ! "$file" == *.log ]]; then
    continue    # Skip non-log files
  fi
  echo "Processing: $file"
  wc -l "$file"
done

# Skip servers that are down
for server in "${servers[@]}"; do
  if ! ping -c 1 -W 1 $server &>/dev/null; then
    echo "⚠️  $server unreachable, skipping"
    continue
  fi
  echo "Deploying to $server..."
  deploy_to $server
done
```

---

## 🔥 Advanced Loop Patterns

### Parallel execution (background processes)

```bash
# Deploy to all servers simultaneously (not one by one)
servers=("web01" "web02" "web03" "web04")

for server in "${servers[@]}"; do
  deploy_to_server "$server" &     # & = run in background
done

wait    # Wait for ALL background jobs to complete
echo "All deployments finished!"
```

### Retry logic

```bash
#!/bin/bash
max_retries=5
attempt=1
url="http://api.example.com/health"

while [ $attempt -le $max_retries ]; do
  echo "Attempt $attempt of $max_retries..."
  
  if curl -sf "$url" > /dev/null; then
    echo "✓ Success on attempt $attempt!"
    break
  fi
  
  echo "  Failed. Waiting before retry..."
  sleep $((attempt * 2))    # Exponential backoff: 2, 4, 6, 8, 10 seconds
  attempt=$((attempt + 1))
done

if [ $attempt -gt $max_retries ]; then
  echo "✗ All $max_retries attempts failed!"
  exit 1
fi
```

### Nested loops (loop inside a loop)

```bash
# Deploy to multiple services across multiple environments
environments=("dev" "staging" "prod")
services=("api" "frontend" "worker")

for env in "${environments[@]}"; do
  echo "=== Environment: $env ==="
  for svc in "${services[@]}"; do
    echo "  Deploying $svc to $env..."
  done
done
```

### Loop with counter and percentage

```bash
files=($(find /var/log -name "*.log" -type f))
total=${#files[@]}
current=0

for file in "${files[@]}"; do
  current=$((current + 1))
  percent=$((current * 100 / total))
  echo "[${percent}%] Processing: $(basename $file)"
  gzip "$file"
done
echo "Done! Compressed $total files."
```

---

## 🎯 Interview Quick Points

- `for` — iterate over a known list or range
- `while` — loop while condition is TRUE
- `until` — loop while condition is FALSE (opposite of while)
- `break` — exit loop entirely
- `continue` — skip to next iteration
- Always quote array expansion: `"${array[@]}"`
- `while IFS= read -r line` is safest for reading files line by line
- C-style `for ((i=0; i<n; i++))` for numeric counter loops
- Use `&` and `wait` for parallel execution
- Combine loops with retry logic for resilient scripts
- `{1..10}` generates a sequence (brace expansion)
