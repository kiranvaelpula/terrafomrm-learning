#!/usr/bin/env python3
"""
Intentionally Vulnerable Flask Application for Security Training
DO NOT USE IN PRODUCTION!
"""

import os
import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

# ❌ SECURITY ISSUE 1: Hardcoded credentials
DATABASE_PASSWORD = "SuperSecret123!"
API_KEY = "sk_live_51234567890abcdef"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

# ❌ SECURITY ISSUE 2: SQL Injection vulnerability
@app.route('/user/<username>')
def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    return str(user)

# ❌ SECURITY ISSUE 3: Command Injection vulnerability
@app.route('/ping')
def ping():
    host = request.args.get('host', 'localhost')
    # Vulnerable to command injection
    result = os.popen(f'ping -c 1 {host}').read()
    return result

# ❌ SECURITY ISSUE 4: Path Traversal vulnerability
@app.route('/read')
def read_file():
    filename = request.args.get('file', 'default.txt')
    # Vulnerable to path traversal
    try:
        with open(f'/var/www/uploads/{filename}', 'r') as f:
            content = f.read()
        return content
    except:
        return "File not found"

# ❌ SECURITY ISSUE 5: XSS (Cross-Site Scripting) vulnerability
@app.route('/hello')
def hello():
    name = request.args.get('name', 'Guest')
    # Vulnerable to XSS - no escaping
    template = f'<h1>Hello {name}!</h1>'
    return render_template_string(template)

# ❌ SECURITY ISSUE 6: Insecure deserialization
@app.route('/load')
def load_data():
    import pickle
    data = request.args.get('data', '')
    # Vulnerable to arbitrary code execution
    obj = pickle.loads(bytes.fromhex(data))
    return str(obj)

# ❌ SECURITY ISSUE 7: Weak cryptography
def encrypt_password(password):
    import hashlib
    # Using deprecated MD5
    return hashlib.md5(password.encode()).hexdigest()

# ❌ SECURITY ISSUE 8: Debug mode enabled
if __name__ == '__main__':
    # Running with debug=True exposes sensitive information
    app.run(host='0.0.0.0', port=8080, debug=True)


# ===========================================================
# SECURE VERSION (for reference)
# ===========================================================

"""
✅ SECURE IMPLEMENTATIONS:

# 1. Use environment variables for secrets
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
API_KEY = os.getenv('API_KEY')

# 2. Use parameterized queries
@app.route('/user/<username>')
def get_user_secure(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    return str(user)

# 3. Validate and sanitize input
@app.route('/ping')
def ping_secure():
    host = request.args.get('host', 'localhost')
    # Validate hostname
    import re
    if not re.match(r'^[a-zA-Z0-9.-]+$', host):
        return "Invalid hostname", 400
    # Use subprocess with list (safer)
    import subprocess
    result = subprocess.run(['ping', '-c', '1', host], 
                          capture_output=True, text=True, timeout=5)
    return result.stdout

# 4. Validate file paths
@app.route('/read')
def read_file_secure():
    filename = request.args.get('file', 'default.txt')
    # Validate filename
    import os.path
    safe_filename = os.path.basename(filename)
    filepath = os.path.join('/var/www/uploads', safe_filename)
    # Check path is within allowed directory
    if not os.path.realpath(filepath).startswith('/var/www/uploads'):
        return "Access denied", 403
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return content
    except:
        return "File not found", 404

# 5. Use auto-escaping templates
@app.route('/hello')
def hello_secure():
    name = request.args.get('name', 'Guest')
    # Flask auto-escapes by default when using templates
    return render_template('hello.html', name=name)

# 6. Don't use pickle with untrusted data
@app.route('/load')
def load_data_secure():
    import json
    data = request.args.get('data', '{}')
    try:
        # Use JSON instead of pickle
        obj = json.loads(data)
        return str(obj)
    except json.JSONDecodeError:
        return "Invalid data", 400

# 7. Use strong cryptography
def encrypt_password_secure(password):
    from werkzeug.security import generate_password_hash
    # Use bcrypt or Argon2
    return generate_password_hash(password, method='pbkdf2:sha256')

# 8. Disable debug in production
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    app.run(host='127.0.0.1', port=8080, debug=debug_mode)
"""
