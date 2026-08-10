# Error Handling and Logging

> **Robust scripts handle errors gracefully and log useful information for debugging. Python's try/except is one of its biggest advantages over shell scripting.**

---

## 📖 Why Error Handling?

Without error handling, your script crashes with ugly tracebacks:
```
Traceback (most recent call last):
  File "deploy.py", line 15, in <module>
    config = json.load(open("config.json"))
FileNotFoundError: [Errno 2] No such file or directory: 'config.json'
```

With error handling:
```
ERROR: Config file not found: config.json
Please create config.json from config.example.json
```

---

## 🛡️ try / except / else / finally

```python
try:
    # Code that MIGHT fail
    risky_operation()
except SpecificError as e:
    # Handle the specific error
    handle_error(e)
except AnotherError as e:
    # Handle another type of error
    handle_differently(e)
else:
    # Runs ONLY if no exception occurred (optional)
    success_actions()
finally:
    # ALWAYS runs, whether error occurred or not (optional)
    cleanup()
```

### Basic Example

```python
# Reading a config file
try:
    with open("config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    print("ERROR: config.json not found")
    print("  Copy config.example.json to config.json and edit it")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"ERROR: config.json has invalid JSON: {e}")
    sys.exit(1)
except PermissionError:
    print("ERROR: No permission to read config.json")
    sys.exit(1)
```

### Common Exceptions in DevOps

```python
# File operations
FileNotFoundError        # File doesn't exist
PermissionError          # No permission to read/write
IsADirectoryError        # Tried to open directory as file
OSError                  # General OS-level error

# Network operations
ConnectionError          # Can't connect to server
TimeoutError             # Connection timed out
requests.exceptions.HTTPError       # HTTP 4xx/5xx
requests.exceptions.ConnectionError # Network unreachable
requests.exceptions.Timeout         # Request timed out

# Data operations
json.JSONDecodeError     # Invalid JSON
yaml.YAMLError           # Invalid YAML
KeyError                 # Dict key doesn't exist
IndexError               # List index out of range
ValueError               # Wrong value type
TypeError                # Wrong argument type

# Subprocess
subprocess.CalledProcessError  # Command returned non-zero
subprocess.TimeoutExpired      # Command took too long

# AWS (boto3)
botocore.exceptions.ClientError      # AWS API error
botocore.exceptions.NoCredentialsError  # No AWS credentials
```

### Practical Error Handling Patterns

```python
# Pattern 1: Retry with backoff
import time

def retry(func, max_attempts=3, delay=2, backoff=2):
    """Retry a function with exponential backoff."""
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts:
                raise    # Re-raise the last exception
            wait = delay * (backoff ** (attempt - 1))
            print(f"  Attempt {attempt} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)

# Usage
def check_api():
    response = requests.get("https://api.example.com/health", timeout=5)
    response.raise_for_status()
    return response.json()

result = retry(check_api, max_attempts=5, delay=2)


# Pattern 2: Graceful degradation
def get_config():
    """Try multiple config sources, fall back gracefully."""
    # Try 1: Environment variable
    config_path = os.environ.get("CONFIG_PATH")
    if config_path and os.path.exists(config_path):
        return load_config(config_path)
    
    # Try 2: Local file
    if os.path.exists("config.yml"):
        return load_config("config.yml")
    
    # Try 3: Default config
    print("WARNING: Using default configuration")
    return {"host": "localhost", "port": 8080}


# Pattern 3: Context manager for cleanup
class TempDirectory:
    """Create temp directory, auto-cleanup on exit."""
    def __enter__(self):
        self.path = tempfile.mkdtemp()
        return self.path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.path)
        return False    # Don't suppress exceptions

# Usage
with TempDirectory() as tmp:
    # Work in temp dir
    # Automatically cleaned up even if exception occurs
    pass
```

### Raising Custom Exceptions

```python
# Define custom exception
class DeploymentError(Exception):
    """Raised when deployment fails."""
    pass

class HealthCheckError(Exception):
    """Raised when health check fails."""
    pass

# Raise it
def deploy(server, version):
    result = subprocess.run(["ssh", server, "deploy", version], ...)
    if result.returncode != 0:
        raise DeploymentError(f"Deploy to {server} failed: {result.stderr}")

# Catch it
try:
    deploy("web01", "v2.0.1")
except DeploymentError as e:
    print(f"Deployment failed: {e}")
    rollback()
```

---

## 📝 Logging Module

`print()` is fine for personal scripts. For production, use `logging`:

### Why logging over print?

| Feature | print() | logging |
|---------|---------|---------|
| Severity levels | ❌ | ✅ (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| Write to file | Manual | Built-in |
| Timestamps | Manual | Automatic |
| Disable easily | Hard | Change one setting |
| Multiple outputs | ❌ | ✅ (screen + file + remote) |
| Filter by level | ❌ | ✅ |

### Basic Setup

```python
import logging

# Simple setup (good for scripts)
logging.basicConfig(
    level=logging.INFO,                              # Minimum level to show
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

# Usage
logger.debug("Detailed info for debugging")    # Hidden (level is INFO)
logger.info("Script started")                   # Shown
logger.warning("Disk usage above 80%")          # Shown
logger.error("Connection to DB failed")         # Shown
logger.critical("System is completely down!")    # Shown
```

### Log to Both Console and File

```python
import logging

def setup_logging(log_file="app.log", level="INFO"):
    """Configure logging to both console and file."""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level))
    
    # Format
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Usage
logger = setup_logging("/var/log/deploy.log", "INFO")
logger.info("Deployment started")
logger.error("Build failed: %s", error_message)    # %s formatting (lazy eval)
```

### Logging with Exception Info

```python
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error("API call failed: %s", e)
    logger.debug("Full traceback:", exc_info=True)  # Includes stack trace at DEBUG level
```

---

## 🛠️ Complete Production Script with Error Handling

```python
#!/usr/bin/env python3
"""Production-ready script with proper error handling and logging."""

import os
import sys
import logging
import subprocess
import time
from datetime import datetime

# ── Logging Setup ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# ── Custom Exceptions ──
class ScriptError(Exception):
    """Base exception for this script."""
    pass

# ── Functions ──
def require_env(var_name):
    """Get required environment variable or exit."""
    value = os.environ.get(var_name)
    if not value:
        logger.error(f"Required environment variable not set: {var_name}")
        sys.exit(1)
    return value

def run_cmd(cmd, timeout=60):
    """Run command with timeout and error handling."""
    logger.debug(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, check=True
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout}s: {' '.join(cmd)}")
        raise ScriptError(f"Timeout: {cmd[0]}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr.strip()}")
        raise ScriptError(f"Failed: {cmd[0]}")

def main():
    """Main entry point."""
    logger.info("=" * 40)
    logger.info("Script started")
    
    try:
        # Validate environment
        api_url = require_env("API_URL")
        
        # Do work
        run_cmd(["docker", "build", "-t", "myapp", "."])
        run_cmd(["docker", "push", "myapp:latest"])
        
        logger.info("✓ Script completed successfully")
        
    except ScriptError as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Interrupted by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 🎯 Interview Quick Points

- Always use `try/except` for operations that can fail (files, network, subprocess)
- Catch **specific** exceptions, never bare `except:` (hides bugs)
- `finally` block always runs (for cleanup — close files, connections)
- `raise` re-throws the current exception to the caller
- Use `logging` module, not `print()`, for production scripts
- Log levels: DEBUG < INFO < WARNING < ERROR < CRITICAL
- `logger.error("msg: %s", var)` — use `%s` not f-strings (lazy evaluation)
- `exc_info=True` in logger includes the full stack trace
- Custom exceptions make error handling clearer
- Retry pattern with exponential backoff for transient failures
- `sys.exit(0)` = success, `sys.exit(1)` = failure
- `KeyboardInterrupt` catches Ctrl+C gracefully
