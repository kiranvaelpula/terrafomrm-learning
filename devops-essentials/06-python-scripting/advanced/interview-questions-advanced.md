# Python DevOps Advanced — Interview Questions

---

## Q1: How would you automate EC2 cost savings?
**A:** Write a Lambda function that stops dev/staging instances at night using boto3 filters on tags. Schedule with EventBridge cron. Also find unattached EBS volumes and old snapshots.

## Q2: How do you build a CLI tool in Python?
**A:** Use `click` library. `@click.group()` for sub-commands, `@click.option()` for flags, `@click.argument()` for positional args.

## Q3: How do you manage Kubernetes from Python?
**A:** Use `kubernetes` library. `config.load_kube_config()` then `CoreV1Api()` for pods/services, `AppsV1Api()` for deployments.

## Q4: How do you handle secrets in Python scripts?
**A:** Never hardcode. Use `os.environ`, AWS Secrets Manager (`boto3`), HashiCorp Vault client, or encrypted .env files.

## Q5: How would you implement a deployment pipeline in Python?
**A:** Build/test/deploy stages as functions. Use subprocess for shell commands, requests for API health checks, paramiko for SSH, slack webhook for notifications.

## Q6: How do you make Python scripts idempotent?
**A:** Check current state before acting (does resource exist?), use create-or-update logic, handle "already exists" errors gracefully.

## Q7: How would you implement log aggregation?
**A:** Parse logs with regex/json, aggregate metrics (error counts, response times), push to monitoring (CloudWatch, Prometheus) or alert on thresholds.

## Q8: How to run Python scripts as systemd services?
**A:** Create a .service unit file pointing to the script, enable it with systemctl. Use `Restart=always` for reliability.

## Q9: How do you test DevOps Python scripts?
**A:** Use `pytest`. Mock external services with `unittest.mock`. Test functions in isolation. Use `moto` for mocking AWS services.

## Q10: Explain decorator pattern in Python with DevOps example.
**A:** Decorators wrap functions. Example: `@retry(max_attempts=3)` adds retry logic. `@timer` measures execution time. Used for cross-cutting concerns.
