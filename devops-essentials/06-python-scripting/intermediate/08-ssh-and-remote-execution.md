# SSH and Remote Execution (paramiko)

> **Automate remote server management — run commands, transfer files, manage configurations over SSH without requiring agents on target servers.**

---

## 📖 Why paramiko?

When you need to run commands on remote servers from Python (like Ansible does under the hood), `paramiko` provides SSH connectivity.

```bash
pip install paramiko
```

---

## 🔧 Basic Connection

```python
import paramiko

# Create SSH client
ssh = paramiko.SSHClient()

# Auto-accept unknown host keys (for lab/testing)
# In production, use known_hosts file
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect with private key
ssh.connect(
    hostname='10.0.1.50',
    port=22,
    username='deploy',
    key_filename='/home/user/.ssh/id_rsa',
    timeout=10
)

# Execute a command
stdin, stdout, stderr = ssh.exec_command('uptime')
output = stdout.read().decode().strip()
error = stderr.read().decode().strip()
exit_code = stdout.channel.recv_exit_status()

print(f"Output: {output}")
print(f"Exit code: {exit_code}")

# Always close
ssh.close()
```

---

## 🛠️ Practical: Multi-Server Deployment

```python
#!/usr/bin/env python3
"""Deploy application to multiple servers via SSH."""

import paramiko
import sys
import os

SERVERS = [
    {"host": "10.0.1.10", "name": "web01"},
    {"host": "10.0.1.11", "name": "web02"},
    {"host": "10.0.1.12", "name": "web03"},
]
SSH_KEY = os.path.expanduser("~/.ssh/deploy_key")
SSH_USER = "deploy"

def run_remote(ssh, command, description=""):
    """Execute command on remote server, return success."""
    if description:
        print(f"    {description}")
    
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_code = stdout.channel.recv_exit_status()
    
    if exit_code != 0:
        error = stderr.read().decode().strip()
        print(f"    ERROR: {error}")
        return False
    return True

def deploy_to_server(server, version):
    """Deploy application to a single server."""
    print(f"\n  [{server['name']}] Deploying v{version}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(server['host'], username=SSH_USER, key_filename=SSH_KEY, timeout=10)
        
        steps = [
            ("cd /opt/app && git fetch origin", "Fetching code..."),
            (f"cd /opt/app && git checkout v{version}", "Switching version..."),
            ("cd /opt/app && pip install -r requirements.txt", "Installing deps..."),
            ("sudo systemctl restart myapp", "Restarting service..."),
        ]
        
        for cmd, desc in steps:
            if not run_remote(ssh, cmd, desc):
                print(f"  [{server['name']}] ✗ FAILED")
                return False
        
        print(f"  [{server['name']}] ✓ SUCCESS")
        return True
        
    except paramiko.AuthenticationException:
        print(f"  [{server['name']}] ✗ Authentication failed")
        return False
    except paramiko.SSHException as e:
        print(f"  [{server['name']}] ✗ SSH error: {e}")
        return False
    except Exception as e:
        print(f"  [{server['name']}] ✗ Error: {e}")
        return False
    finally:
        ssh.close()

def main():
    version = sys.argv[1] if len(sys.argv) > 1 else None
    if not version:
        print("Usage: deploy.py <version>")
        sys.exit(1)
    
    print(f"Deploying v{version} to {len(SERVERS)} servers")
    
    results = []
    for server in SERVERS:
        success = deploy_to_server(server, version)
        results.append((server['name'], success))
    
    # Summary
    print("\n" + "=" * 40)
    failed = [name for name, ok in results if not ok]
    if failed:
        print(f"❌ Failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("✅ All servers deployed successfully")

if __name__ == "__main__":
    main()
```

---

## 📁 File Transfer (SFTP)

```python
# Upload file
sftp = ssh.open_sftp()
sftp.put('/local/path/app.tar.gz', '/remote/path/app.tar.gz')

# Download file
sftp.get('/remote/path/logs/app.log', '/local/path/app.log')

# List remote directory
files = sftp.listdir('/opt/app/releases')

sftp.close()
```

---

## 🎯 Interview Quick Points

- `paramiko` = Python SSH library (no agent needed on remote)
- `ssh.connect()` establishes connection (key or password auth)
- `exec_command()` runs command, returns stdin/stdout/stderr
- `recv_exit_status()` gets the command's exit code
- `open_sftp()` for file transfers (put/get)
- Always close connections in finally block
- Catch `AuthenticationException` and `SSHException` separately
- For many servers, consider `concurrent.futures` for parallel execution
- For complex multi-server work, use Ansible instead
