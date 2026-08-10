# Networking and API Calls

> **Shell scripts often interact with APIs, check network connectivity, and automate HTTP operations. curl is your swiss army knife.**

---

## 📖 curl — The HTTP Swiss Army Knife

curl is the most important networking tool in DevOps scripting. It makes HTTP requests from the command line.

### Basic Requests

```bash
# GET request (default)
curl https://api.example.com/users

# Common options you'll use constantly:
curl -s       # Silent mode (no progress bar)
curl -f       # Fail silently (no output on HTTP errors)
curl -L       # Follow redirects (301/302)
curl -o file  # Save output to file
curl -O       # Save with original filename
curl -k       # Skip SSL certificate verification (testing only!)
curl -v       # Verbose (shows headers, useful for debugging)

# Combination you'll use most (silent, fail on error):
curl -sf https://api.example.com/health
```

### GET with Parameters

```bash
# Query parameters
curl -s "https://api.example.com/users?page=1&limit=10"

# Custom headers
curl -s \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" \
  https://api.example.com/data
```

### POST Requests

```bash
# POST with JSON body
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"webserver","env":"production"}' \
  https://api.example.com/servers

# POST with variables in JSON
NAME="web-05"
ENV="staging"
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"${NAME}\",\"environment\":\"${ENV}\"}" \
  https://api.example.com/servers

# POST form data
curl -s -X POST \
  -d "username=admin&password=secret" \
  https://api.example.com/login

# POST with file upload
curl -s -X POST \
  -F "file=@/path/to/deploy.tar.gz" \
  https://api.example.com/upload
```

### PUT and DELETE

```bash
# PUT (update)
curl -s -X PUT \
  -H "Content-Type: application/json" \
  -d '{"replicas": 5}' \
  https://api.example.com/deployments/myapp

# DELETE
curl -s -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  https://api.example.com/servers/old-server-01
```

### Getting Response Details

```bash
# Get ONLY the HTTP status code
status=$(curl -s -o /dev/null -w "%{http_code}" https://api.example.com/health)
echo "Status: $status"
# -o /dev/null = discard body
# -w "%{http_code}" = print status code

# Get response time
time=$(curl -s -o /dev/null -w "%{time_total}" https://api.example.com/)
echo "Response time: ${time}s"

# Get multiple metrics
curl -s -o /dev/null -w "\
  HTTP Code: %{http_code}\n\
  Time Total: %{time_total}s\n\
  Time Connect: %{time_connect}s\n\
  Size Download: %{size_download} bytes\n" \
  https://api.example.com/

# Save headers to file
curl -s -D headers.txt https://api.example.com/ > /dev/null
cat headers.txt

# Get response body AND status code
response=$(curl -s -w "\n%{http_code}" https://api.example.com/users)
body=$(echo "$response" | head -n -1)
status=$(echo "$response" | tail -n 1)
```

---

## 🔄 Working with JSON Responses (jq)

`jq` is the standard tool for parsing JSON in shell scripts:

```bash
# Install: apt install jq

# Pretty print JSON
curl -s https://api.github.com/users/octocat | jq .

# Extract a field
curl -s https://api.github.com/users/octocat | jq -r '.login'

# Extract nested field
curl -s https://api.example.com/server | jq -r '.config.database.host'

# Extract from array
curl -s https://api.github.com/users/octocat/repos | jq -r '.[0].name'

# Filter array
curl -s https://api.example.com/servers | jq -r '.[] | select(.status=="running") | .name'

# Multiple fields
curl -s https://api.example.com/servers | jq -r '.[] | "\(.name) \(.ip) \(.status)"'

# Count items
curl -s https://api.example.com/servers | jq '. | length'
```

---

## 🌐 Network Connectivity Testing

```bash
# Check if host is reachable
ping -c 1 -W 2 google.com &>/dev/null && echo "UP" || echo "DOWN"

# Check if TCP port is open
# Method 1: nc (netcat)
nc -zv -w 3 hostname 80        # -z = scan, -v = verbose, -w = timeout

# Method 2: Bash built-in (no extra tools needed)
timeout 3 bash -c "echo > /dev/tcp/hostname/80" 2>/dev/null && echo "Port open" || echo "Port closed"

# Method 3: Check multiple ports
for port in 22 80 443 8080; do
  if timeout 2 bash -c "echo > /dev/tcp/myserver/$port" 2>/dev/null; then
    echo "  Port $port: OPEN"
  else
    echo "  Port $port: CLOSED"
  fi
done

# DNS lookup
dig +short example.com                # IP address
dig +short -x 8.8.8.8                 # Reverse DNS
nslookup example.com                   # Full lookup
host example.com                       # Simple lookup

# Trace network path
traceroute google.com
mtr --report google.com               # Better traceroute

# Check listening ports on local machine
ss -tlnp                              # TCP listening ports with process
ss -tlnp | grep :8080                 # What's on port 8080
```

---

## 🛠️ Complete API Integration Scripts

### Health Check Script

```bash
#!/bin/bash
set -euo pipefail

# ── Configuration ──
declare -A ENDPOINTS
ENDPOINTS[API]="https://api.example.com/health"
ENDPOINTS[Frontend]="https://app.example.com"
ENDPOINTS[Auth]="https://auth.example.com/status"
ENDPOINTS[Database]="http://internal-db:5432/health"

TIMEOUT=5
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# ── Check each endpoint ──
failed=()

for name in "${!ENDPOINTS[@]}"; do
  url="${ENDPOINTS[$name]}"
  
  start=$(date +%s%N)
  status=$(curl -sf -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null || echo "000")
  end=$(date +%s%N)
  duration=$(( (end - start) / 1000000 ))    # Milliseconds
  
  if [ "$status" = "200" ]; then
    echo "  ✓ $name — ${status} (${duration}ms)"
  else
    echo "  ✗ $name — ${status} (${duration}ms)"
    failed+=("$name (HTTP $status)")
  fi
done

# ── Alert if any failed ──
if [ ${#failed[@]} -gt 0 ]; then
  message="🚨 *Health Check Failed*\n"
  for f in "${failed[@]}"; do
    message+="• $f\n"
  done
  
  if [ -n "$SLACK_WEBHOOK" ]; then
    curl -sf -X POST "$SLACK_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{\"text\":\"$(echo -e "$message")\"}"
  fi
  
  exit 1
fi

echo "  All endpoints healthy ✓"
```

### Webhook/ChatOps Integration

```bash
#!/bin/bash
# Send deployment notification to Slack

send_slack() {
  local color=$1
  local title=$2
  local message=$3
  
  local payload=$(cat << EOF
{
  "attachments": [{
    "color": "$color",
    "title": "$title",
    "text": "$message",
    "footer": "Deploy Bot | $(date '+%Y-%m-%d %H:%M:%S')"
  }]
}
EOF
)
  
  curl -sf -X POST "$SLACK_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# Usage
send_slack "good" "✅ Deployment Successful" "v2.0.1 deployed to production by $USER"
send_slack "danger" "❌ Deployment Failed" "Build failed at testing stage"
```

---

## 📥 Downloading and Transferring Files

```bash
# Download with progress
curl -L -o filename.tar.gz https://releases.example.com/app-v2.tar.gz

# Download only if newer than local copy
curl -z local_file.txt -o local_file.txt https://example.com/file.txt

# Resume interrupted download
curl -C - -O https://example.com/large-file.iso

# Upload via SFTP
curl -T localfile.txt sftp://server/path/remote.txt --user "user:pass"

# wget alternative (simpler for downloads)
wget -q https://example.com/file.tar.gz         # Quiet download
wget -c https://example.com/large.iso            # Resume download
wget --mirror https://example.com/docs/          # Mirror a website
```

---

## 🎯 Interview Quick Points

- `curl -sf` = silent + fail on HTTP errors (perfect for scripts)
- `curl -o /dev/null -w "%{http_code}"` extracts just the status code
- Always use `--max-time` to prevent hanging on unresponsive servers
- `jq` parses JSON: `curl ... | jq -r '.field'`
- `nc -zv host port` checks if a port is open
- `/dev/tcp/host/port` is a bash built-in for TCP connectivity
- Process substitution: `<(curl -s url)` treats response as a file
- Use `timeout` command wrapper for network operations
- For webhooks: POST to Slack/Teams URL with JSON payload
- Always quote URLs in scripts (they may contain special characters)
- `curl -v` for debugging (shows full request/response headers)
