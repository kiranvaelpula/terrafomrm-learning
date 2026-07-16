# Basic Git Commands

Master the essential Git commands for daily development.

## Repository Commands

### git init
\\\ash
git init
git init -b main
\\\

### git clone
\\\ash
git clone https://github.com/user/repo.git
git clone -b branch-name url
\\\

## File Tracking

### git status
\\\ash
git status
git status -s
\\\

### git add
\\\ash
git add file.txt
git add .
git add -A
\\\

### git commit
\\\ash
git commit -m 'message'
git commit -am 'message'
\\\

## Viewing History

### git log
\\\ash
git log
git log --oneline
git log --graph --all
\\\

### git diff
\\\ash
git diff
git diff --staged
git diff commit1 commit2
\\\

## Undoing Changes

### git restore
\\\ash
git restore file.txt
git restore --staged file.txt
\\\

### git reset
\\\ash
git reset HEAD~1
git reset --soft HEAD~1
git reset --hard HEAD~1
\\\

## Best Practices
1. Commit often
2. Write clear messages
3. Review before committing
4. Use .gitignore
5. Use branches

**Previous:** [Installation](02-installation-configuration.md) | **Next:** [Workflow](04-git-workflow.md)
