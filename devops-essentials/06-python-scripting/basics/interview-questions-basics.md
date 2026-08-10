# Python for DevOps — Basic Interview Questions

---

## Q1: Why use Python over shell scripting?
**A:** Better error handling (try/except), complex data structures, cross-platform, cleaner syntax for long scripts, rich library ecosystem (boto3, requests, etc.).

## Q2: How do you run a shell command from Python?
**A:** `subprocess.run(["command", "arg"], capture_output=True, text=True)`. Use `check=True` to raise on failure.

## Q3: How do you read environment variables?
**A:** `os.environ.get("VAR_NAME", "default_value")` — returns None or default if not set.

## Q4: Difference between `json.load()` and `json.loads()`?
**A:** `load()` reads from a file object, `loads()` parses a string.

## Q5: How do you handle exceptions?
**A:** `try/except` blocks. Catch specific exceptions, use `finally` for cleanup, `raise` to re-throw.

## Q6: What is a virtual environment and why use it?
**A:** Isolated Python environment per project. Prevents dependency conflicts. Create with `python3 -m venv env`.

## Q7: How do you parse YAML in Python?
**A:** `import yaml; data = yaml.safe_load(open("file.yaml"))`. Always use `safe_load`.

## Q8: Explain list comprehension with an example.
**A:** `[x*2 for x in range(5) if x > 1]` → `[4, 6, 8]`. Concise way to build filtered/transformed lists.

## Q9: How do you make an API call?
**A:** `import requests; r = requests.get("url"); data = r.json()`. Check `r.status_code`.

## Q10: What does `if __name__ == "__main__":` do?
**A:** Code inside only runs when script is executed directly, not when imported as a module.
