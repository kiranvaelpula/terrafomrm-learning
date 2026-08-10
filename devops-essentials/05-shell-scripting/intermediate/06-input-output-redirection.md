# Input/Output Redirection

> **Redirection controls where command input comes from and output goes to — files, other commands, or /dev/null.**

---

## 📖 What is Redirection?

Every Linux command has three data streams:

```
                    ┌─────────────────┐
   stdin (0)        │                 │      stdout (1)
  Keyboard ────────▶│    Command      │─────────────▶ Screen
                    │                 │
                    └────────┬────────┘
                             │
                             │ stderr (2)
                             ▼
                           Screen
```

| Stream | File Descriptor | Default Source/Destination | Purpose |
|--------|----------------|---------------------------|---------|
| stdin | 0 | Keyboard | Input to the command |
| stdout | 1 | Terminal screen | Normal output |
| stderr | 2 | Terminal screen | Error messages |

**Redirection** changes these defaults — send output to a file, read input from a file, or connect commands together.

---

## 📤 Output Redirection (stdout)

### `>` — Redirect stdout to file (OVERWRITE)

```bash
# Creates file if doesn't exist, OVERWRITES if it does
echo "hello" > output.txt
ls -la /var/log > filelist.txt
date > timestamp.txt

# ⚠️ WARNING: > destroys existing content!
echo "first line" > file.txt      # File contains: "first line"
echo "second line" > file.txt     # File now ONLY contains: "second line"
```

### `>>` — Redirect stdout to file (APPEND)

```bash
# Adds to end of file without destroying existing content
echo "line 1" >> log.txt
echo "line 2" >> log.txt
echo "line 3" >> log.txt
# File now has all three lines

# DevOps use: Logging
echo "[$(date)] Deployment started" >> /var/log/deploy.log
echo "[$(date)] Version: v2.0.1"   >> /var/log/deploy.log
```

---

## 📤 Error Redirection (stderr)

### `2>` — Redirect stderr to file

```bash
# Normal output goes to screen, errors go to file
ls /nonexistent 2> errors.txt
cat errors.txt    # "ls: cannot access '/nonexistent': No such file or directory"

# Discard errors silently
find / -name "secret.txt" 2> /dev/null
# You only see the results, not "Permission denied" errors
```

### `2>>` — Append stderr to file

```bash
command1 2>> error.log
command2 2>> error.log     # Errors accumulate in log
```

---

## 🔀 Combining stdout and stderr

```bash
# Method 1: Redirect both to SAME file
command > all_output.log 2>&1
# Explanation:
#   > all_output.log    → stdout goes to file
#   2>&1                → stderr goes wherever stdout is going (the file)

# Method 2: Shorthand (bash only)
command &> all_output.log           # Same as above, shorter
command &>> all_output.log          # Append version

# Method 3: Send each to DIFFERENT files
command > stdout.log 2> stderr.log

# Method 4: Discard everything (complete silence)
command > /dev/null 2>&1
command &> /dev/null                # Shorthand
```

**Real-world examples:**
```bash
# Run a deployment script, capture all output
./deploy.sh > /var/log/deploy.log 2>&1

# Check if command exists (discard all output, just check exit code)
if command -v docker &> /dev/null; then
  echo "Docker is installed"
fi

# Background process with logging
nohup ./server.sh > /var/log/server.log 2>&1 &
```

---

## 📥 Input Redirection (stdin)

### `<` — Read input from a file

```bash
# Instead of typing, read from a file
wc -l < /etc/passwd              # Count lines (file content as input)
sort < unsorted.txt              # Sort the file
mysql -u root < setup.sql        # Feed SQL file to mysql

# Difference:
wc -l /etc/passwd                # Output: "45 /etc/passwd" (shows filename)
wc -l < /etc/passwd              # Output: "45" (no filename — it doesn't know)
```

### `<<` — Here Document (multi-line input)

Provide multi-line text as input to a command:

```bash
# Syntax: command << DELIMITER
#         content
#         DELIMITER

cat << EOF
Hello $USER!
Today is $(date +%A).
You are in: $PWD
EOF
# Variables and commands ARE expanded

# Use 'EOF' (quoted) to prevent expansion
cat << 'EOF'
This is literal: $USER $(date)
No expansion happens here.
EOF

# Practical: Create a config file
cat << EOF > /etc/nginx/conf.d/app.conf
server {
    listen 80;
    server_name ${DOMAIN};
    
    location / {
        proxy_pass http://localhost:${APP_PORT};
    }
}
EOF

# Practical: Run multiple SQL commands
mysql -u root << EOF
CREATE DATABASE IF NOT EXISTS myapp;
GRANT ALL ON myapp.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
EOF

# Practical: SSH multiple commands
ssh user@server << 'EOF'
cd /opt/app
git pull origin main
docker-compose down
docker-compose up -d
echo "Done!"
EOF
```

### `<<<` — Here String (single-line input)

```bash
# Feed a string as input to a command
grep "hello" <<< "hello world"         # Output: hello world
wc -w <<< "one two three four"         # Output: 4

# Useful when you have a variable and need to pipe it
line="name:john:25:developer"
IFS=: read -r name first age role <<< "$line"
echo "$name, $first, $age, $role"
```

---

## 🔗 Pipes (`|`)

Pipes connect the stdout of one command to the stdin of the next. This is one of the most powerful concepts in Linux.

```
┌──────────┐  stdout   ┌──────────┐  stdout   ┌──────────┐
│ Command1 │──────────▶│ Command2 │──────────▶│ Command3 │───▶ Screen
└──────────┘   (pipe)  └──────────┘   (pipe)  └──────────┘
```

```bash
# Basic: filter output
ls -la | grep ".log"                     # List only log files
ps aux | grep nginx                      # Find nginx processes
cat /etc/passwd | wc -l                  # Count users

# Chain multiple pipes
cat /var/log/syslog | grep "error" | sort | uniq -c | sort -rn | head -10
# Explanation:
#   cat syslog         → read log file
#   grep "error"       → keep only error lines
#   sort               → sort alphabetically
#   uniq -c            → count duplicates
#   sort -rn           → sort by count (highest first)
#   head -10           → show top 10

# DevOps examples
docker ps | grep "Exited" | awk '{print $1}' | xargs docker rm
# Find exited containers → get their IDs → remove them

kubectl get pods | grep -v Running | grep -v NAME
# Show only pods that are NOT running

netstat -tlnp | grep :80
# Find what's listening on port 80
```

### `tee` — Output to BOTH screen AND file

```bash
# Normal: output goes to file only
echo "hello" > file.txt    # Nothing shown on screen

# With tee: output goes to BOTH screen and file
echo "hello" | tee file.txt           # Shows "hello" AND writes to file
echo "world" | tee -a file.txt        # -a = append mode

# DevOps use: See deployment output AND save it
./deploy.sh 2>&1 | tee /var/log/deploy.log
# You see everything live AND it's saved to a log file

# Multiple files
echo "log entry" | tee file1.txt file2.txt file3.txt
```

---

## 🔧 Advanced Redirection

### File descriptors

```bash
# Open file for writing on descriptor 3
exec 3> custom_output.txt
echo "This goes to fd 3" >&3
echo "This also goes to fd 3" >&3
exec 3>&-                              # Close fd 3

# Open file for reading on descriptor 4
exec 4< input_data.txt
read -u 4 line1                        # Read from fd 4
read -u 4 line2
exec 4<&-                              # Close fd 4
```

### Process substitution `<(command)`

Treat command output as if it were a file:

```bash
# Compare two command outputs without temp files
diff <(ls dir1) <(ls dir2)

# Compare sorted files without creating temp files
diff <(sort file1.txt) <(sort file2.txt)

# Feed multiple inputs to a command
paste <(cut -d: -f1 /etc/passwd) <(cut -d: -f3 /etc/passwd)
```

---

## 📊 Redirection Quick Reference

| Syntax | Meaning |
|--------|---------|
| `> file` | Redirect stdout to file (overwrite) |
| `>> file` | Redirect stdout to file (append) |
| `2> file` | Redirect stderr to file (overwrite) |
| `2>> file` | Redirect stderr to file (append) |
| `&> file` | Redirect BOTH stdout+stderr (overwrite) |
| `&>> file` | Redirect BOTH stdout+stderr (append) |
| `2>&1` | Send stderr to same place as stdout |
| `< file` | Read input from file |
| `<< WORD` | Here document (multi-line input) |
| `<<< "string"` | Here string (single-line input) |
| `cmd1 \| cmd2` | Pipe stdout of cmd1 to stdin of cmd2 |
| `> /dev/null` | Discard output (black hole) |

---

## 🛠️ DevOps Practical Examples

### Logging with timestamps

```bash
#!/bin/bash
LOG="/var/log/myapp/deploy.log"

# Everything in this script goes to log AND screen
exec > >(tee -a "$LOG") 2>&1

echo "[$(date)] Deployment started"
echo "[$(date)] Pulling latest code..."
git pull
echo "[$(date)] Restarting service..."
systemctl restart myapp
echo "[$(date)] Deployment complete"
```

### Separate success and error logs

```bash
./build.sh > /var/log/build_output.log 2> /var/log/build_errors.log

if [ -s /var/log/build_errors.log ]; then
  echo "Build had errors!"
  cat /var/log/build_errors.log
fi
```

### Feeding data to multiple commands

```bash
# Process a file with multiple tools simultaneously
cat access.log | tee \
  >(grep "500" > server_errors.log) \
  >(grep "404" > not_found.log) \
  >(wc -l > total_requests.txt) \
  > /dev/null
```

---

## 🎯 Interview Quick Points

- `>` overwrites, `>>` appends
- `2>` redirects stderr, `&>` redirects both stdout and stderr
- `2>&1` merges stderr into stdout (order matters!)
- `/dev/null` is the "black hole" — discards anything written to it
- `|` (pipe) connects stdout → stdin between commands
- `tee` splits output to file AND screen simultaneously
- `<<` here document provides multi-line input
- `<<<` here string provides single-line input
- Process substitution `<()` treats command output as a file
- `exec >` redirects all subsequent output in the script
