# Process Management

> **Understanding processes is critical for DevOps — managing services, killing stuck processes, monitoring resources, and scheduling tasks.**

---

## 📖 What is a Process?

A process is a **running instance of a program**. Every command you run becomes a process with its own:
- PID (Process ID) — unique identifier
- Parent PID (PPID) — the process that started it
- State (Running, Sleeping, Stopped, Zombie)
- Resource usage (CPU, memory)

```
┌──────────────────┐
│    init (PID 1)  │       ← First process (systemd on modern Linux)
└────────┬─────────┘
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌──────┐
│sshd  │  │nginx │         ← System services
│PID 50│  │PID 80│
└──┬───┘  └──┬───┘
   ▼         ▼
┌──────┐  ┌──────┐
│bash  │  │worker│         ← Child processes
│PID200│  │PID 81│
└──┬───┘  └──────┘
   ▼
┌──────┐
│ vim  │                    ← Your command
│PID300│
└──────┘
```

---

## 🔍 Viewing Processes

### ps — Process snapshot

```bash
# Basic (only YOUR processes in current terminal)
ps

# ALL processes, detailed (most common usage)
ps aux
# a = all users
# u = user-oriented format
# x = include processes without a terminal

# Output columns explained:
# USER  PID  %CPU  %MEM  VSZ    RSS    TTY  STAT  START  TIME  COMMAND
# root  1    0.0   0.1   16900  10240  ?    Ss    Aug08  0:05  /sbin/init

# Full format (shows PPID — parent process ID)
ps -ef

# Filter specific process
ps aux | grep nginx
ps aux | grep "[n]ginx"        # Trick: excludes the grep command itself

# Process tree (shows parent-child relationships)
ps auxf                        # Forest format
pstree                         # Visual tree
pstree -p                      # With PIDs
```

### STAT column meanings:
```
S  = Sleeping (waiting for something)
R  = Running (actively using CPU)
T  = Stopped (suspended, e.g., Ctrl+Z)
Z  = Zombie (finished but parent hasn't collected exit status)
D  = Uninterruptible sleep (usually I/O wait)

s  = Session leader
+  = In foreground process group
l  = Multi-threaded
<  = High priority
N  = Low priority
```

### top / htop — Real-time monitoring

```bash
# top — built-in real-time monitor
top
# Key commands inside top:
#   q     = quit
#   P     = sort by CPU
#   M     = sort by Memory
#   k     = kill a process (enter PID)
#   1     = show individual CPU cores
#   h     = help

# Filter in top
top -p 1234,5678               # Monitor specific PIDs only
top -u nginx                   # Only processes owned by nginx user

# htop — better interactive monitor (may need: apt install htop)
htop
# Has colors, mouse support, easier to use
```

### Other process viewing commands

```bash
# Find PID by name
pgrep nginx                    # Returns PIDs of nginx processes
pgrep -f "python app.py"      # Search full command line
pidof nginx                    # PID of exact process name

# Count processes
pgrep -c nginx                 # How many nginx processes running

# What's using a specific port?
ss -tlnp | grep :80            # What's on port 80
lsof -i :8080                  # Which process uses port 8080

# What files does a process have open?
lsof -p 1234                   # Files open by PID 1234
```

---

## 🔄 Foreground and Background Processes

### Understanding foreground vs background

```bash
# FOREGROUND — blocks your terminal until complete
sleep 60                       # Terminal is stuck for 60 seconds
# You can't type anything else

# BACKGROUND — runs without blocking terminal
sleep 60 &                     # & = run in background
# Terminal is free immediately, process runs silently
# Output: [1] 12345  (job number and PID)
```

### Job Control

```bash
# Run in background
./long_script.sh &
[1] 45678                      # Job 1, PID 45678

# List background jobs
jobs
# [1]+  Running    ./long_script.sh &

# Bring background job to foreground
fg %1                          # Bring job 1 to foreground

# Suspend (pause) a foreground process
# Press Ctrl+Z while process is running
# [1]+  Stopped    ./long_script.sh

# Resume in background
bg %1

# Resume in foreground
fg %1
```

### Keep processes alive after terminal closes

```bash
# nohup — "no hangup": process survives terminal close
nohup ./server.sh &
# Output goes to nohup.out by default

# With custom log file
nohup ./server.sh > /var/log/server.log 2>&1 &

# disown — detach from current shell
./server.sh &
disown %1              # Now it won't die when shell exits
```

---

## ☠️ Killing Processes

### Signals

When you "kill" a process, you're sending it a SIGNAL:

| Signal | Number | Meaning | Use Case |
|--------|--------|---------|----------|
| SIGTERM | 15 | Please stop gracefully | Default kill (saves data, closes connections) |
| SIGKILL | 9 | FORCE stop immediately | When SIGTERM doesn't work |
| SIGHUP | 1 | Hangup / reload config | Reload nginx config without restart |
| SIGSTOP | 19 | Pause process | Temporarily suspend |
| SIGCONT | 18 | Resume paused process | Resume after SIGSTOP |
| SIGINT | 2 | Interrupt (Ctrl+C) | Stop foreground process |

### Killing Commands

```bash
# By PID
kill 12345                     # Send SIGTERM (graceful — process can cleanup)
kill -15 12345                 # Same as above (explicit SIGTERM)
kill -9 12345                  # Send SIGKILL (force — no cleanup, last resort!)

# By name
killall nginx                  # Kill ALL processes named "nginx"
pkill nginx                    # Same, but uses pattern matching
pkill -f "python app.py"      # Kill by full command line match

# Graceful then force pattern
kill 12345                     # Try graceful first
sleep 5                        # Wait 5 seconds
kill -0 12345 2>/dev/null && kill -9 12345   # If still alive, force kill
# kill -0 checks if process exists without actually killing it

# Kill all of a user's processes
pkill -u baduser               # Kill everything owned by baduser
```

### When to use SIGTERM vs SIGKILL:

```bash
# ALWAYS try SIGTERM first (kill or kill -15)
# - Process can save data
# - Close database connections
# - Remove lock files
# - Write final log entry

# Use SIGKILL (-9) ONLY when:
# - Process ignores SIGTERM
# - Process is stuck/frozen
# - You've already waited and it won't die
```

### Reload config without restart (SIGHUP):

```bash
# Nginx: reload config without downtime
kill -HUP $(cat /var/run/nginx.pid)
# OR
nginx -s reload                # Same thing, more readable

# Systemd equivalent
systemctl reload nginx
```

---

## 📅 Scheduled Tasks (Cron)

Cron runs scripts automatically at scheduled times.

### Crontab Format

```
┌─────── Minute (0-59)
│ ┌─────── Hour (0-23)
│ │ ┌─────── Day of month (1-31)
│ │ │ ┌─────── Month (1-12)
│ │ │ │ ┌─────── Day of week (0-7, 0 and 7 = Sunday)
│ │ │ │ │
* * * * * command to execute
```

### Editing Crontab

```bash
crontab -e             # Edit your crontab
crontab -l             # List your cron jobs
crontab -r             # Remove ALL your cron jobs (careful!)
sudo crontab -e        # Edit root's crontab
sudo crontab -u nginx -e    # Edit another user's crontab
```

### Cron Examples

```bash
# Every minute
* * * * * /opt/scripts/health-check.sh

# Every 5 minutes
*/5 * * * * /opt/scripts/monitor.sh

# Every hour at minute 0
0 * * * * /opt/scripts/cleanup-temp.sh

# Daily at 2:30 AM
30 2 * * * /opt/scripts/backup.sh

# Every Monday at 9 AM
0 9 * * 1 /opt/scripts/weekly-report.sh

# First day of every month at midnight
0 0 1 * * /opt/scripts/monthly-cleanup.sh

# Weekdays (Mon-Fri) at 6 PM
0 18 * * 1-5 /opt/scripts/daily-summary.sh

# Every 15 minutes during business hours
*/15 9-17 * * 1-5 /opt/scripts/business-check.sh
```

### Cron Best Practices

```bash
# Always use full paths in cron (no $PATH available)
0 2 * * * /usr/bin/python3 /opt/scripts/backup.py

# Redirect output to log
0 2 * * * /opt/scripts/backup.sh >> /var/log/cron-backup.log 2>&1

# Use MAILTO for email notifications
MAILTO=devops@example.com
0 2 * * * /opt/scripts/backup.sh

# Lock file to prevent overlap (if script takes longer than interval)
*/5 * * * * flock -n /tmp/monitor.lock /opt/scripts/monitor.sh
```

---

## 🛠️ systemd Service Management

```bash
# View service status
systemctl status nginx
systemctl is-active nginx           # Just "active" or "inactive"
systemctl is-enabled nginx          # Will it start on boot?

# Start/Stop/Restart
systemctl start nginx
systemctl stop nginx
systemctl restart nginx             # Stop then start
systemctl reload nginx              # Reload config without stopping

# Enable/Disable at boot
systemctl enable nginx              # Start on boot
systemctl disable nginx             # Don't start on boot
systemctl enable --now nginx        # Enable AND start immediately

# View logs
journalctl -u nginx                 # All logs for nginx
journalctl -u nginx --since today   # Today's logs only
journalctl -u nginx -f              # Follow (live tail)
journalctl -u nginx --no-pager      # Don't paginate
```

---

## 🎯 Interview Quick Points

- `ps aux` shows all running processes with details
- `top`/`htop` for real-time monitoring
- `kill` sends SIGTERM (graceful), `kill -9` sends SIGKILL (force)
- Always try graceful kill first, force only as last resort
- `&` runs process in background
- `nohup` prevents process death when terminal closes
- `jobs`, `fg`, `bg` for job control
- Cron format: `MIN HOUR DAY MONTH WEEKDAY command`
- `*/5` means "every 5 units"
- Use `pgrep`/`pkill` to find/kill by name
- `lsof -i :port` shows what's using a port
- `systemctl` manages services on modern Linux
- Zombie processes: finished but parent hasn't read exit status
