# Building CLI Tools with Click

> **Build professional command-line tools for your DevOps team using Python's Click library. Custom CLIs replace complex shell scripts and provide better UX.**

---

## 📖 Why Build CLI Tools?

Instead of remembering: `ssh deploy@server "cd /opt && git pull && pip install -r req.txt && systemctl restart app"`

Your team runs: `devops deploy staging --version 2.0.1`

```bash
pip install click
```

---

## 🎯 Basic CLI Tool

```python
#!/usr/bin/env python3
"""Simple CLI tool with Click."""

import click

@click.command()
@click.argument('name')                                    # Required positional arg
@click.option('--greeting', '-g', default='Hello', help='Greeting to use')
@click.option('--count', '-c', default=1, type=int, help='Number of greetings')
def hello(name, greeting, count):
    """Greet someone NAME times."""
    for _ in range(count):
        click.echo(f"{greeting}, {name}!")

if __name__ == '__main__':
    hello()
```

```bash
$ python hello.py World
Hello, World!

$ python hello.py Kiran --greeting Hi --count 3
Hi, Kiran!
Hi, Kiran!
Hi, Kiran!

$ python hello.py --help
Usage: hello.py [OPTIONS] NAME

  Greet someone NAME times.

Options:
  -g, --greeting TEXT  Greeting to use
  -c, --count INTEGER  Number of greetings
  --help              Show this message and exit.
```

---

## 🛠️ Multi-Command CLI (like kubectl, docker)

```python
#!/usr/bin/env python3
"""DevOps CLI tool with multiple commands."""

import click
import subprocess
import sys
import os

@click.group()           # Creates a command group (parent)
@click.version_option(version='1.0.0')
def cli():
    """DevOps deployment and management tool."""
    pass


@cli.command()
@click.argument('environment', type=click.Choice(['dev', 'staging', 'prod']))
@click.option('--version', '-v', required=True, help='Version to deploy')
@click.option('--dry-run', is_flag=True, help='Show what would be done')
@click.option('--skip-tests', is_flag=True, help='Skip post-deploy tests')
def deploy(environment, version, dry_run, skip_tests):
    """Deploy application to an environment."""
    
    if environment == 'prod' and not dry_run:
        if not click.confirm('⚠️  Deploy to PRODUCTION?'):
            click.echo('Cancelled.')
            return
    
    click.echo(f"{'[DRY RUN] ' if dry_run else ''}Deploying v{version} to {environment}...")
    
    if dry_run:
        click.echo("  Would: pull image, update deployment, run health check")
        return
    
    # Actual deployment steps
    with click.progressbar(length=4, label='Deploying') as bar:
        # Step 1: Pull image
        bar.update(1)
        # Step 2: Update deployment
        bar.update(1)
        # Step 3: Wait for rollout
        bar.update(1)
        # Step 4: Health check
        bar.update(1)
    
    click.secho(f"✓ Deployed v{version} to {environment}", fg='green')


@cli.command()
@click.argument('service')
def status(service):
    """Check service status."""
    result = subprocess.run(
        ["systemctl", "is-active", service],
        capture_output=True, text=True
    )
    if result.stdout.strip() == "active":
        click.secho(f"✓ {service} is running", fg='green')
    else:
        click.secho(f"✗ {service} is stopped", fg='red')
        sys.exit(1)


@cli.command()
@click.option('--namespace', '-n', default='default', help='Kubernetes namespace')
def pods(namespace):
    """List Kubernetes pods."""
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", namespace, "--no-headers"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        click.echo(result.stdout)
    else:
        click.secho(f"Error: {result.stderr}", fg='red')


if __name__ == '__main__':
    cli()
```

```bash
$ python devops-cli.py --help
$ python devops-cli.py deploy staging --version 2.0.1
$ python devops-cli.py deploy prod --version 2.0.1 --dry-run
$ python devops-cli.py status nginx
$ python devops-cli.py pods -n production
```

---

## 📦 Making it Installable

Create `setup.py` or `pyproject.toml` to install as a system command:

```python
# setup.py
from setuptools import setup

setup(
    name='devops-cli',
    version='1.0.0',
    py_modules=['devops_cli'],
    install_requires=['click'],
    entry_points={
        'console_scripts': [
            'devops=devops_cli:cli',    # 'devops' command runs cli() function
        ],
    },
)
```

```bash
pip install -e .    # Install in development mode
devops deploy staging --version 2.0.1    # Now works system-wide!
```

---

## 🎯 Interview Quick Points

- `@click.command()` for single commands, `@click.group()` for sub-commands
- `@click.argument()` for required positional args
- `@click.option()` for flags (--name, -n)
- `click.echo()` for output, `click.secho()` for colored output
- `click.confirm()` for yes/no prompts
- `click.progressbar()` for progress display
- `type=click.Choice([...])` restricts values to a set
- `is_flag=True` makes boolean options (--verbose, --dry-run)
- Install as CLI with `entry_points` in setup.py
- Click auto-generates `--help` from docstrings
