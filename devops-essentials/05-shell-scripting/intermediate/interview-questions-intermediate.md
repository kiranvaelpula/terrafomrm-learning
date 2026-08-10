# Shell Scripting Intermediate — Interview Questions

---

## Q1: Explain the difference between `>` and `>>`?
**A:** `>` overwrites the file, `>>` appends to it.

## Q2: What is `2>&1`?
**A:** Redirects stderr (fd 2) to wherever stdout (fd 1) is going, combining both streams.

## Q3: How does `set -euo pipefail` help?
**A:** `-e` exits on error, `-u` treats unset variables as errors, `-o pipefail` makes pipes fail if any command fails. Together they form "strict mode."

## Q4: How do you find and kill a process by name?
**A:** `pkill -f "process_name"` or `ps aux | grep name` then `kill PID`.

## Q5: What is a trap in bash?
**A:** `trap` catches signals and runs cleanup code — e.g., `trap cleanup EXIT` runs a function when the script exits.

## Q6: Explain awk vs sed vs grep.
**A:** `grep` = filter lines by pattern. `sed` = find/replace in streams. `awk` = column-based processing and calculations.

## Q7: How do you schedule a script to run every 5 minutes?
**A:** Add to crontab: `*/5 * * * * /path/to/script.sh`

## Q8: What does `nohup` do?
**A:** Keeps a process running after the terminal is closed. Output goes to nohup.out by default.

## Q9: How do you pass output of one command as input to another?
**A:** Using pipes: `command1 | command2`. Stdout of command1 becomes stdin of command2.

## Q10: How to check if a command exists before using it?
**A:** `command -v docker >/dev/null 2>&1 || echo "docker not found"`
