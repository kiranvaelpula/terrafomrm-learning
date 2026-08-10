# Working with OS and Subprocess

> **Execute system commands, manage files/directories, and interact with the operating system from Python. This bridges the gap between Python and shell scripting.**

---

## 📖 Why subprocess?

When you need to run a shell command from Python (like `docker build`, `kubectl apply`, or `systemctl restart`), you use the `subprocess` module. It's the Python equivalent of typing commands in a terminal.

---

## ⚙️ subprocess Module — Running Shell Commands

### Basic Usage: subprocess.run()

```python
import subprocess

# Simple command
result = subprocess.run(["ls", "-la"], capture_output=True, text=True)

print(result.stdout)          # Standard output (what you'd see on screen)
print(result.stderr)          # Error output
print(result.returncode)      # Exit code (0 = success)
```

**Understanding the arguments:**
```python
subprocess.run(
    ["command", "arg1", "arg2"],  # Command as a LIST (preferred, safer)
    capture_output=True,          # Capture stdout and stderr
    text=True,                    # Return strings instead of bytes
    check=False,                  # Don't raise exception on failure (default)
    timeout=30,                   # Kill command if takes >30 seconds
    cwd="/opt/app",              # Run in this directory
    env={"PATH": "/usr/bin"}     # Custom environment variables
)
```

### Running common DevOps commands

```python
import subprocess
import sys

def run_command(cmd, check=True):
    """Run a command and return result. Raise on failure if check=True."""
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"  ERROR: {result.stderr.strip()}")
        sys.exit(1)
    
    return result


# Docker commands
run_command(["docker", "build", "-t", "myapp:latest", "."])
run_command(["docker", "push", "registry.example.com/myapp:latest"])

# Kubernetes commands
result = run_command(["kubectl", "get", "pods", "-n", "production", "-o", "json"])
pods = json.loads(result.stdout)

# Git commands
result = run_command(["git", "rev-parse", "HEAD"], check=False)
commit = result.stdout.strip()
print(f"Current commit: {commit}")

# Systemctl
run_command(["sudo", "systemctl", "restart", "nginx"])
```

### check=True — Automatic error handling

```python
# With check=True, Python raises an exception if command fails
try:
    subprocess.run(
        ["docker", "build", "-t", "myapp", "."],
        check=True,              # Raises CalledProcessError on failure
        capture_output=True,
        text=True
    )
    print("Build succeeded!")
except subprocess.CalledProcessError as e:
    print(f"Build failed! Exit code: {e.returncode}")
    print(f"Error output: {e.stderr}")
    sys.exit(1)
```

### Shell mode (use with caution)

```python
# shell=True — passes command as a string to /bin/sh
# AVOID when possible (security risk if user input is involved)

# When you need pipes or shell features:
result = subprocess.run(
    "ps aux | grep nginx | wc -l",
    shell=True,
    capture_output=True,
    text=True
)
nginx_count = int(result.stdout.strip())

# Better alternative: pipe in Python
ps = subprocess.run(["ps", "aux"], capture_output=True, text=True)
nginx_lines = [l for l in ps.stdout.splitlines() if "nginx" in l]
nginx_count = len(nginx_lines)
```

**⚠️ Security warning:**
```python
# NEVER do this with user input:
user_input = input("Enter filename: ")
subprocess.run(f"cat {user_input}", shell=True)  # ❌ User could type "; rm -rf /"

# SAFE: use list form (arguments are escaped automatically)
subprocess.run(["cat", user_input])              # ✅ Safe
```

---

## 📂 os Module — System Interaction

### Environment Variables

```python
import os

# Read environment variables
home = os.environ.get("HOME")                    # Returns None if not set
db_host = os.environ.get("DB_HOST", "localhost") # Returns default if not set
api_key = os.environ["API_KEY"]                  # Raises KeyError if not set

# Check if variable exists
if "SLACK_WEBHOOK" in os.environ:
    webhook = os.environ["SLACK_WEBHOOK"]

# Set environment variable (for THIS process and children)
os.environ["APP_ENV"] = "production"
os.environ["LOG_LEVEL"] = "DEBUG"

# Get all environment variables
for key, value in os.environ.items():
    if key.startswith("DB_"):
        print(f"  {key}={value}")
```

### File and Directory Operations

```python
import os

# Path checking
os.path.exists("/etc/nginx")          # True if exists (file or dir)
os.path.isfile("config.yml")          # True if it's a regular file
os.path.isdir("/var/log")             # True if it's a directory
os.path.getsize("app.log")            # File size in bytes

# Path manipulation
os.path.join("/opt", "app", "config.yml")    # "/opt/app/config.yml" (OS-aware)
os.path.basename("/var/log/nginx/access.log") # "access.log"
os.path.dirname("/var/log/nginx/access.log")  # "/var/log/nginx"
os.path.splitext("report.tar.gz")            # ("report.tar", ".gz")
os.path.abspath("./script.py")               # Full absolute path

# Directory operations
os.getcwd()                           # Current working directory
os.listdir("/var/log")                # List directory contents (names only)
os.makedirs("/opt/app/logs", exist_ok=True)  # Create nested dirs (like mkdir -p)
os.remove("temp_file.txt")           # Delete a file
os.rmdir("empty_dir")               # Delete empty directory

# Walking directory tree
for root, dirs, files in os.walk("/opt/app"):
    for file in files:
        full_path = os.path.join(root, file)
        if file.endswith(".log"):
            print(f"Log file: {full_path}")
```

### pathlib — Modern Path Handling (Python 3.4+)

```python
from pathlib import Path

# Create Path objects
config = Path("/etc/nginx/nginx.conf")
project = Path.cwd() / "src" / "app.py"    # Use / operator to join

# Check properties
config.exists()         # True/False
config.is_file()        # True
config.is_dir()         # False
config.name             # "nginx.conf"
config.stem             # "nginx"
config.suffix           # ".conf"
config.parent           # Path("/etc/nginx")

# Read/Write files
content = config.read_text()                # Read entire file
Path("output.txt").write_text("hello\n")    # Write to file

# Find files (glob patterns)
log_files = list(Path("/var/log").glob("*.log"))         # All .log in dir
all_yaml = list(Path("/opt").rglob("*.yaml"))            # Recursive search

# Create directories
Path("backups/daily").mkdir(parents=True, exist_ok=True)
```

---

## 🔍 shutil — High-Level File Operations

```python
import shutil

# Copy file
shutil.copy("source.txt", "dest.txt")             # Copy file + permissions
shutil.copy2("source.txt", "dest.txt")            # Copy + metadata (timestamps)

# Copy entire directory tree
shutil.copytree("src_dir", "dest_dir")

# Move/rename file or directory
shutil.move("old_location/file.txt", "new_location/file.txt")

# Delete directory tree (like rm -rf)
shutil.rmtree("/tmp/build")                       # ⚠️ DANGEROUS — no confirmation!

# Disk usage
usage = shutil.disk_usage("/")
print(f"Total: {usage.total // (1024**3)}GB")
print(f"Used:  {usage.used // (1024**3)}GB")
print(f"Free:  {usage.free // (1024**3)}GB")

# Create archive (tar.gz, zip)
shutil.make_archive("backup_2026", "gztar", "/opt/app/data")
# Creates: backup_2026.tar.gz

# Extract archive
shutil.unpack_archive("backup.tar.gz", "/opt/restore/")
```

---

## 🛠️ Practical DevOps Examples

### Deploy script

```python
#!/usr/bin/env python3
"""Simple deployment script."""

import subprocess
import sys
import os
from datetime import datetime


def run(cmd, cwd=None):
    """Run command, exit on failure."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"  FAILED: {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()


def main():
    app_dir = "/opt/myapp"
    version = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not version:
        print("Usage: deploy.py <version>")
        sys.exit(1)
    
    print(f"[{datetime.now():%H:%M:%S}] Deploying v{version}")
    
    # Pull latest code
    run(["git", "fetch", "origin"], cwd=app_dir)
    run(["git", "checkout", f"v{version}"], cwd=app_dir)
    
    # Install dependencies
    run(["pip", "install", "-r", "requirements.txt"], cwd=app_dir)
    
    # Restart service
    run(["sudo", "systemctl", "restart", "myapp"])
    
    # Verify
    import time
    time.sleep(3)
    result = subprocess.run(
        ["curl", "-sf", "http://localhost:8080/health"],
        capture_output=True
    )
    
    if result.returncode == 0:
        print(f"[{datetime.now():%H:%M:%S}] ✓ Deployment successful!")
    else:
        print("✗ Health check failed! Rolling back...")
        run(["git", "checkout", "HEAD~1"], cwd=app_dir)
        run(["sudo", "systemctl", "restart", "myapp"])
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## 🎯 Interview Quick Points

- `subprocess.run()` is the modern way to run shell commands
- Use LIST form `["cmd", "arg"]` not string form (safer)
- `capture_output=True, text=True` to get string output
- `check=True` raises exception on non-zero exit code
- Avoid `shell=True` unless you need pipes/shell features
- `os.environ.get("VAR", "default")` safely reads env vars
- `os.path.join()` builds paths (OS-aware slashes)
- `os.makedirs(path, exist_ok=True)` = `mkdir -p`
- `pathlib.Path` is modern alternative to os.path
- `shutil` for copy/move/delete directories
- Always use `cwd` parameter instead of `os.chdir()`
- Never use `shell=True` with user input (command injection risk)
