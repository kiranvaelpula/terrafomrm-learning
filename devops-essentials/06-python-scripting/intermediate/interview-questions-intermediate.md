# Python DevOps Intermediate — Interview Questions

---

## Q1: How do you manage AWS resources using Python?
**A:** Use `boto3` library. `boto3.client('ec2')` for low-level API, `boto3.resource('ec2')` for high-level object-oriented access.

## Q2: How do you make a POST request with authentication?
**A:** `requests.post(url, json=data, headers={"Authorization": f"Bearer {token}"})`

## Q3: How do you SSH into a server from Python?
**A:** Use `paramiko`. Connect with `ssh.connect()`, run commands with `exec_command()`, transfer files with `open_sftp()`.

## Q4: How do you handle pagination in AWS API calls?
**A:** Use paginators: `paginator = client.get_paginator('list_objects_v2')` then iterate pages.

## Q5: How would you stop all dev EC2 instances at night?
**A:** Filter instances by tag (Environment=dev) and state (running), then call `stop_instances()`. Schedule with Lambda + EventBridge.

## Q6: How do you interact with Docker from Python?
**A:** `import docker; client = docker.from_env()`. Then `client.containers.run()`, `.list()`, `.stop()`.

## Q7: How do you monitor system resources in Python?
**A:** Use `psutil` — `psutil.cpu_percent()`, `psutil.virtual_memory()`, `psutil.disk_usage('/')`.

## Q8: How would you implement retry logic for an API call?
**A:** Use a loop with exponential backoff, or the `tenacity` library with `@retry` decorator.

## Q9: How do you send a Slack alert from Python?
**A:** POST to Slack webhook URL: `requests.post(webhook_url, json={"text": "message"})`

## Q10: What's the difference between `boto3.client` and `boto3.resource`?
**A:** Client returns raw dict responses (low-level). Resource returns Python objects with methods (high-level, easier to use).
