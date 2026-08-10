# Python Fundamentals for DevOps

> **Core Python concepts you need for writing DevOps automation scripts. This isn't a full Python course — it's the 20% you'll use 80% of the time.**

---

## 📖 Variables and Data Types

Python is **dynamically typed** — you don't declare types, Python figures it out.

### Strings (text)

```python
# Strings — most common in DevOps (hostnames, paths, messages)
hostname = "web-server-01"
ip_address = "10.0.1.50"
environment = 'production'     # Single or double quotes both work

# f-strings (formatted strings) — Python 3.6+ — USE THESE ALWAYS
port = 8080
url = f"http://{hostname}:{port}/health"
print(url)   # http://web-server-01:8080/health

message = f"Deployed v{version} to {environment} at {datetime.now()}"

# Multi-line strings (triple quotes)
config = """
server {{
    listen {port};
    server_name {hostname};
}}
"""

# String methods you'll use constantly
path = "/var/log/nginx/access.log"
path.startswith("/var")        # True
path.endswith(".log")          # True
path.split("/")                # ['', 'var', 'log', 'nginx', 'access.log']
"  hello  ".strip()            # "hello" (remove whitespace)
"hello world".replace("world", "python")   # "hello python"
"hello".upper()                # "HELLO"
"HELLO".lower()                # "hello"
"error" in "error: disk full"  # True (contains check)
```

### Numbers

```python
# Integers
port = 8080
replicas = 3
max_retries = 5

# Floats (decimals)
cpu_usage = 75.5
threshold = 0.85

# Arithmetic
total = replicas * 2          # 6
remaining = 100 - cpu_usage   # 24.5
percent = used / total * 100  # Division gives float
integer_div = 10 // 3         # 3 (floor division)
remainder = 10 % 3            # 1 (modulo)
power = 2 ** 10               # 1024
```

### Booleans

```python
is_running = True
debug_mode = False
is_production = environment == "production"    # Comparison returns bool

# Truthy/Falsy values:
# False: 0, "", [], {}, None, False
# True: everything else (non-zero, non-empty)

if servers:          # True if list is NOT empty
    deploy(servers)
```

---

## 📋 Data Structures

### Lists (ordered, mutable — like arrays)

```python
# Create
servers = ["web01", "web02", "web03", "db01"]
ports = [80, 443, 8080, 3306]

# Access (0-indexed)
first = servers[0]        # "web01"
last = servers[-1]        # "db01"
subset = servers[1:3]     # ["web02", "web03"] (slice)

# Modify
servers.append("web04")           # Add to end
servers.insert(0, "lb01")         # Insert at position
servers.remove("db01")            # Remove by value
popped = servers.pop()            # Remove and return last item
servers.extend(["cache01", "cache02"])  # Add multiple

# Check
"web01" in servers                # True
len(servers)                      # Number of items

# Loop
for server in servers:
    print(f"Checking {server}...")

# Loop with index
for i, server in enumerate(servers):
    print(f"{i+1}. {server}")

# List comprehension (powerful one-liner to create lists)
# [expression for item in iterable if condition]
web_servers = [s for s in servers if s.startswith("web")]
ports_str = [str(p) for p in ports]
uppercase = [s.upper() for s in servers]
```

### Dictionaries (key-value pairs — like JSON objects)

```python
# Create (most used data structure in DevOps)
config = {
    "host": "10.0.1.50",
    "port": 3306,
    "database": "production",
    "ssl": True,
    "timeout": 30
}

# Access
host = config["host"]                    # Raises KeyError if missing
host = config.get("host")               # Returns None if missing
host = config.get("host", "localhost")   # Returns default if missing

# Modify
config["port"] = 5432                    # Update value
config["user"] = "admin"                 # Add new key
del config["ssl"]                        # Delete key
config.pop("timeout", None)             # Remove and return (None if missing)

# Check
"host" in config                         # True
"password" in config                     # False

# Loop
for key, value in config.items():
    print(f"  {key}: {value}")

for key in config:                       # Just keys
    print(key)

# Nested dictionaries (very common — think JSON/YAML)
deployment = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": "nginx",
        "namespace": "production"
    },
    "spec": {
        "replicas": 3,
        "template": {
            "spec": {
                "containers": [
                    {"name": "nginx", "image": "nginx:1.25"}
                ]
            }
        }
    }
}

# Access nested
name = deployment["metadata"]["name"]   # "nginx"
replicas = deployment["spec"]["replicas"]  # 3
```

### Tuples (ordered, IMMUTABLE — can't change after creation)

```python
# Use for fixed data that shouldn't change
coordinates = (40.7128, -74.0060)
rgb_red = (255, 0, 0)
server_info = ("web01", "10.0.1.5", 8080)

# Unpacking (assign multiple variables at once)
hostname, ip, port = server_info
print(f"{hostname} at {ip}:{port}")

# Return multiple values from function
def get_server_status(name):
    return "running", 99.5, 1024    # Returns tuple

status, uptime, memory = get_server_status("web01")
```

### Sets (unique items, unordered — great for deduplication)

```python
# Unique items only
active_users = {"alice", "bob", "charlie", "alice"}  # alice appears once
print(active_users)   # {'alice', 'bob', 'charlie'}

# Set operations
admins = {"alice", "dave"}
developers = {"bob", "charlie", "dave"}

admins & developers          # Intersection: {'dave'}
admins | developers          # Union: {'alice', 'bob', 'charlie', 'dave'}
admins - developers          # Difference: {'alice'}

# Deduplicate a list
ips = ["10.0.1.1", "10.0.1.2", "10.0.1.1", "10.0.1.3"]
unique_ips = list(set(ips))  # ['10.0.1.1', '10.0.1.2', '10.0.1.3']
```

---

## 🔄 Control Flow

### if / elif / else

```python
status_code = 503

if status_code == 200:
    print("OK")
elif status_code == 404:
    print("Not Found")
elif status_code >= 500:
    print("Server Error — needs investigation!")
else:
    print(f"Unexpected status: {status_code}")

# Comparison operators: ==, !=, >, <, >=, <=
# Logical operators: and, or, not

# Practical example
environment = "production"
cpu_usage = 85

if environment == "production" and cpu_usage > 80:
    send_alert("High CPU in production!")
elif cpu_usage > 90:
    send_alert("Critical CPU!")
```

### for loops

```python
# Loop through a list
servers = ["web01", "web02", "web03"]
for server in servers:
    print(f"Deploying to {server}...")

# Loop through a range of numbers
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 11):     # 1 through 10
    print(i)

for i in range(0, 100, 10):  # 0, 10, 20, ... 90 (step by 10)
    print(f"Progress: {i}%")

# Loop through dictionary
config = {"host": "db01", "port": 5432, "ssl": True}
for key, value in config.items():
    print(f"  {key} = {value}")

# enumerate — loop with index
for index, server in enumerate(servers, start=1):
    print(f"  {index}. {server}")

# zip — loop through two lists together
names = ["web01", "web02", "web03"]
ips = ["10.0.1.1", "10.0.1.2", "10.0.1.3"]
for name, ip in zip(names, ips):
    print(f"  {name} → {ip}")
```

### while loops

```python
# Retry logic (very common in DevOps)
import time

max_retries = 5
attempt = 0

while attempt < max_retries:
    attempt += 1
    print(f"Attempt {attempt}/{max_retries}...")
    
    if check_health():
        print("Service is healthy!")
        break
    
    if attempt < max_retries:
        wait = attempt * 2    # Exponential backoff
        print(f"  Retrying in {wait}s...")
        time.sleep(wait)
else:
    # 'else' on while runs if loop completed WITHOUT break
    print("All retries exhausted!")
    sys.exit(1)
```

---

## 🛠️ Functions

```python
def deploy(server, version, restart=True):
    """
    Deploy application to a server.
    
    Args:
        server: hostname or IP of target server
        version: version string to deploy
        restart: whether to restart service (default: True)
    
    Returns:
        bool: True if deployment succeeded
    """
    print(f"Deploying v{version} to {server}...")
    
    if restart:
        print(f"  Restarting service on {server}")
    
    return True


# Call with positional args
deploy("web01", "2.0.1")

# Call with keyword args (more readable)
deploy(server="web02", version="2.0.1", restart=False)

# Multiple return values
def get_server_info(hostname):
    """Return server details as tuple."""
    ip = "10.0.1.5"
    port = 8080
    status = "healthy"
    return ip, port, status

ip, port, status = get_server_info("web01")


# *args and **kwargs (variable arguments)
def log_event(message, *tags, **metadata):
    """Log an event with optional tags and metadata."""
    print(f"[{message}] tags={tags}, meta={metadata}")

log_event("deployed", "production", "v2", app="myapp", user="kiran")
```

---

## 📂 File Operations

```python
# Read entire file
with open("/etc/hosts", "r") as f:
    content = f.read()           # Entire file as one string
print(content)

# Read line by line (memory efficient for large files)
with open("servers.txt", "r") as f:
    for line in f:
        server = line.strip()    # Remove trailing newline
        print(f"Server: {server}")

# Read all lines into a list
with open("servers.txt") as f:
    servers = [line.strip() for line in f if line.strip()]

# Write to file (creates/overwrites)
with open("output.txt", "w") as f:
    f.write("Line 1\n")
    f.write("Line 2\n")

# Append to file
with open("deploy.log", "a") as f:
    f.write(f"[{datetime.now()}] Deployed v2.0.1\n")

# Write multiple lines
lines = ["web01", "web02", "web03"]
with open("servers.txt", "w") as f:
    f.writelines(f"{line}\n" for line in lines)
```

**Why `with open()` instead of just `open()`?**
The `with` statement automatically closes the file when the block ends, even if an error occurs. Without it, you might leave files open (resource leak).

---

## 🔑 Important Python Concepts

### None (like null in other languages)

```python
result = None    # "No value" or "not set yet"

if result is None:
    print("No result")

# Common pattern: optional function parameters
def connect(host, port=None):
    if port is None:
        port = 5432    # Default
```

### Type checking

```python
isinstance(42, int)           # True
isinstance("hello", str)      # True
isinstance([1,2], list)       # True
type(42)                      # <class 'int'>
```

### String formatting methods

```python
name = "web01"
port = 8080

# f-string (PREFERRED — Python 3.6+)
url = f"http://{name}:{port}"

# .format() (older)
url = "http://{}:{}".format(name, port)

# % formatting (oldest — avoid)
url = "http://%s:%d" % (name, port)
```

---

## 🎯 Interview Quick Points

- Python uses **indentation** (4 spaces) for code blocks — not braces `{}`
- `f"string {variable}"` for string formatting (f-strings)
- Lists are mutable `[]`, tuples are immutable `()`
- Dictionaries `{}` store key-value pairs (like JSON)
- `with open()` ensures files are properly closed
- Functions use `def`, return `None` by default
- List comprehensions: `[x*2 for x in range(5) if x > 1]`
- `for key, value in dict.items()` to loop over dictionaries
- `enumerate()` gives index + value in loops
- `zip()` combines two lists element-by-element
- `None` is Python's "no value" (check with `is None`, not `== None`)
- Everything is an object in Python
