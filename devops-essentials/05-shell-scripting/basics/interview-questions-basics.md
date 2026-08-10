# Shell Scripting Basics — Interview Questions

---

## Q1: What is a shebang line?
**A:** `#!/bin/bash` — it tells the OS which interpreter to use to execute the script.

## Q2: How do you make a script executable?
**A:** `chmod +x script.sh`, then run with `./script.sh`

## Q3: What is the difference between `$@` and `$*`?
**A:** `$@` treats each argument as separate quoted strings. `$*` treats all arguments as a single string. In most cases, use `"$@"`.

## Q4: How do you check if a file exists?
**A:** `if [ -f "filename" ]; then ... fi`

## Q5: What does `set -e` do?
**A:** Causes the script to exit immediately if any command returns a non-zero exit code.

## Q6: Difference between single quotes and double quotes?
**A:** Single quotes (`' '`) are literal — no variable expansion. Double quotes (`" "`) allow variable and command expansion.

## Q7: How do you capture command output in a variable?
**A:** `result=$(command)` — command substitution.

## Q8: What is `$?`?
**A:** The exit status of the last executed command (0 = success, non-zero = failure).

## Q9: Difference between `[ ]` and `[[ ]]`?
**A:** `[[ ]]` is bash-specific, supports regex, pattern matching, and doesn't require quoting variables. `[ ]` is POSIX-compatible but more limited.

## Q10: How do you read a file line by line?
**A:** `while IFS= read -r line; do echo "$line"; done < file.txt`

## Q11: What is the difference between `source script.sh` and `./script.sh`?
**A:** `source` runs in the current shell (variables persist). `./script.sh` runs in a subshell (variables don't affect parent).

## Q12: How do you pass arguments to a function?
**A:** Call with `func_name arg1 arg2`, access inside with `$1`, `$2`, `$#`.

## Q13: What does `2>&1` mean?
**A:** Redirects stderr (file descriptor 2) to stdout (file descriptor 1), combining both outputs.

## Q14: How do you debug a shell script?
**A:** Use `bash -x script.sh` or add `set -x` inside the script to print each command before execution.

## Q15: What is an exit code and why is it important?
**A:** A number (0-255) returned by every command. 0 = success, non-zero = failure. Used in conditionals and CI/CD pipelines to determine if a step passed.
