# Shell Scripting Advanced — Interview Questions

---

## Q1: How do you prevent a script from running multiple instances?
**A:** Use a lock file. Check if it exists before running, create it on start, remove it via `trap EXIT`.

## Q2: Explain `set -euo pipefail`.
**A:** `-e` exits on error, `-u` errors on undefined variables, `-o pipefail` fails pipe if any command fails. It's the standard "strict mode."

## Q3: How do you parse command-line arguments in bash?
**A:** Use a `while` loop with `case` for long options, or `getopts` for short options. Check `$#` for argument count.

## Q4: How do you run commands in parallel and wait for all to finish?
**A:** Run with `&` (background), then use `wait` to wait for all background processes.

## Q5: How do you make an API call and check the response?
**A:** `status=$(curl -s -o /dev/null -w "%{http_code}" URL)` then check if status equals 200.

## Q6: What is a trap and when would you use it?
**A:** `trap` catches signals (EXIT, ERR, SIGINT). Used for cleanup like removing temp files, releasing locks, or logging on unexpected exit.

## Q7: How to debug a complex shell script?
**A:** Use `set -x` for tracing, `bash -x script.sh`, add strategic echo/log statements, check `$?` after critical commands.

## Q8: Explain process substitution.
**A:** `<(command)` treats command output as a file. Example: `diff <(sort file1) <(sort file2)` compares sorted versions.

## Q9: How do you handle secrets in shell scripts?
**A:** Never hardcode. Use environment variables, secret managers (AWS Secrets Manager, Vault), or read from protected files with strict permissions.

## Q10: Write a one-liner to find the top 5 largest files in a directory.
**A:** `find /path -type f -exec du -h {} + | sort -rh | head -5`
