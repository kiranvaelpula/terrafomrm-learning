# Git Interview Questions - Basics Level

Comprehensive interview questions and answers for Git fundamentals.

---

## Conceptual Questions

### Q1: What is Git?

**Answer:**

Git is a distributed version control system (DVCS) that tracks changes in source code during software development. Created by Linus Torvalds in 2005, Git enables multiple developers to work on the same project simultaneously while maintaining a complete history of all changes.

**Key characteristics:**
- **Distributed**: Every developer has a complete copy of the repository
- **Fast**: Most operations are local
- **Data integrity**: Everything is checksummed (SHA-1 hash)
- **Branching**: Lightweight and fast branch operations

---

### Q2: What is version control and why do we need it?

**Answer:**

Version control is a system that records changes to files over time, allowing you to recall specific versions later.

**Benefits:**
- **Track history**: See what changed, when, and by whom
- **Collaboration**: Multiple people can work simultaneously
- **Backup**: Project history is preserved
- **Experimentation**: Try new ideas without risk
- **Rollback**: Revert to previous working versions

**Without version control:**
```
project-v1.js
project-v2.js
project-v2-final.js
project-v2-REALLY-final.js
```

**With version control:**
```
project.js (all versions tracked internally)
```

---

### Q3: Explain the three states in Git

**Answer:**

Files in Git exist in three states:

**1. Modified**
- File has been changed
- Changes are in working directory
- Not yet staged for commit

**2. Staged**
- Modified file is marked for next commit
- Changes are in staging area (index)
- Ready to be committed

**3. Committed**
- Data is safely stored in Git repository
- Snapshot is permanent in history

**Workflow:**
```
Working Directory  →  Staging Area  →  Git Repository
   (Modified)         (Staged)         (Committed)
```

---

### Q4: What is the difference between Git and GitHub?

**Answer:**

**Git:**
- Version control system (software)
- Runs locally on your computer
- Open-source
- Command-line tool
- Created by Linus Torvalds

**GitHub:**
- Web-based hosting service for Git repositories
- Cloud platform
- Company (owned by Microsoft)
- Adds collaboration features (pull requests, issues, CI/CD)
- One of many hosting options (GitLab, Bitbucket are alternatives)

**Analogy:**
- Git is like Microsoft Word (software)
- GitHub is like Google Docs (platform that uses the software)

---

### Q5: Explain the staging area (index)

**Answer:**

The staging area (also called index) is an intermediate area between the working directory and the repository where changes are prepared before committing.

**Purpose:**
- **Selective commits**: Choose which changes to include
- **Logical grouping**: Build meaningful commits
- **Review opportunity**: Check what will be committed

**Example:**
```bash
# Modified 3 files
touch file1.txt file2.txt file3.txt

# Stage only 2 files
git add file1.txt file2.txt

# Commit just those 2
git commit -m "Add files 1 and 2"

# file3.txt is still untracked
```


### Q6: What is a commit in Git?

**Answer:**

A commit is a snapshot of your project at a specific point in time. It's the fundamental unit in Git's version history.

**Commit contains:**
- **Snapshot**: Complete state of all tracked files
- **Metadata**: 
  - Author name and email
  - Timestamp
  - Commit message
  - Unique SHA-1 hash (40-character identifier)
  - Parent commit(s)

**Example:**
```bash
git commit -m "Add user authentication feature"

# Creates commit like:
# commit a3f8d92c1e4b5f6a7b8c9d0e1f2g3h4i5j6k7l8m
# Author: John Doe <john@example.com>
# Date:   Mon Jan 15 10:30:00 2024
#
#     Add user authentication feature
```

---

### Q7: What is a branch in Git?

**Answer:**

A branch is a lightweight movable pointer to a commit. It allows you to diverge from the main development line without affecting it.

**Characteristics:**
- **Lightweight**: Just a 41-byte file (40-char SHA-1 + newline)
- **Fast**: Creating/deleting branches is instant
- **Independent**: Work doesn't affect other branches
- **Mergeable**: Changes can be integrated back

**Visual representation:**
```
main:     A -- B -- C
                   \
feature:            D -- E
```

**Common uses:**
- New features
- Bug fixes
- Experiments
- Multiple versions

---

### Q8: What is HEAD in Git?

**Answer:**

HEAD is a pointer that indicates your current location in the Git repository. It typically points to the branch you're currently on.

**States of HEAD:**

**1. Normal (attached):**
```bash
HEAD → main → commit-C
```

**2. Detached:**
```bash
HEAD → commit-B (not on any branch)
```

**Examples:**
```bash
# HEAD points to main branch
$ cat .git/HEAD
ref: refs/heads/main

# After detaching
$ git checkout a3f8d92
$ cat .git/HEAD
a3f8d92c1e4b5f6a7b8c9d0e1f2g3h4i5j6k7l8m
```

---

## Practical Questions

### Q9: How do you initialize a Git repository?

**Answer:**

```bash
# Method 1: Initialize in current directory
git init

# Method 2: Create directory and initialize
git init my-project

# Method 3: Initialize with specific branch name
git init -b main
```

**What happens:**
- Creates `.git` directory
- Sets up Git structure (objects, refs, HEAD)
- Repository is ready to track files

**Verification:**
```bash
ls -la
# Should see .git/ directory

git status
# Should show "On branch main/master"
```

---

### Q10: How do you check the status of your repository?

**Answer:**

```bash
# Basic status
git status

# Short format
git status -s
git status --short

# With branch info
git status -sb
```

**Output interpretation:**
```bash
$ git status
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   index.html      # Staged

Changes not staged for commit:
  (use "git add <file>..." to update)
  (use "git restore <file>..." to discard)
        modified:   app.js          # Modified

Untracked files:
  (use "git add <file>..." to include)
        style.css                   # Untracked
```

**Short format codes:**
- `??` = Untracked
- `A` = Added (staged new file)
- `M` = Modified
- `D` = Deleted
- `R` = Renamed

---

### Q11: What's the difference between `git add .` and `git add -A`?

**Answer:**

Both stage all changes, but with subtle differences:

**`git add .`**
- Stages files in current directory and subdirectories
- Respects your current location
- Doesn't stage deletions in parent directories

**`git add -A` or `git add --all`**
- Stages all changes in entire repository
- Works from any directory
- Stages everything: new, modified, and deleted

**Example:**
```bash
# In subdirectory
cd src/
echo "new" > file.txt
rm ../old.txt

git add .       # Stages src/file.txt only
git add -A      # Stages src/file.txt AND deletion of old.txt
```

**Best practice:**
```bash
# Most common: Stage everything
git add -A

# Selective: Stage specific files
git add file1.txt file2.txt
```

---

### Q12: How do you create a commit?

**Answer:**

```bash
# Method 1: With message
git commit -m "Add user login feature"

# Method 2: Open editor for detailed message
git commit

# Method 3: Skip staging (tracked files only)
git commit -a -m "Update all tracked files"
git commit -am "Update all tracked files"

# Method 4: Multi-line message
git commit -m "Add authentication" -m "Implemented JWT and session management"
```

**Good commit message format:**
```bash
# Short (50 chars or less) summary

# Blank line

# Detailed explanation if needed (wrap at 72 chars)
# - What changed
# - Why it changed
# - Any side effects
```

**Examples:**
```bash
# ✅ Good
git commit -m "Fix null pointer in payment validation"

# ❌ Bad
git commit -m "fixed stuff"
```

---

### Q13: How do you view commit history?

**Answer:**

```bash
# Full log
git log

# One line per commit
git log --oneline

# With graph
git log --graph --oneline --all

# Last N commits
git log -5
git log -n 5

# By date
git log --since="2 weeks ago"
git log --after="2024-01-01"

# By author
git log --author="John"

# Search messages
git log --grep="bug fix"

# Show changes
git log -p
git log --patch

# File history
git log -- filename.txt

# Pretty format
git log --pretty=format:"%h - %an, %ar : %s"
```

**Example output:**
```bash
$ git log --oneline --graph --all
* a3f8d92 (HEAD -> main) Add feature
* b2e7c81 Fix bug
* c1f6a90 Initial commit
```

---

### Q14: What's the difference between `git diff`, `git diff --staged`, and `git diff HEAD`?

**Answer:**

**`git diff`**
- Shows unstaged changes
- Compares working directory with staging area
```bash
# Changes not yet staged
git diff
```

**`git diff --staged` (or `--cached`)**
- Shows staged changes
- Compares staging area with last commit
```bash
# Changes ready to be committed
git diff --staged
```

**`git diff HEAD`**
- Shows all changes (staged + unstaged)
- Compares working directory with last commit
```bash
# All changes since last commit
git diff HEAD
```

**Example:**
```bash
# Modify file
echo "change" >> file.txt

git diff           # Shows the change

# Stage file
git add file.txt

git diff           # Shows nothing
git diff --staged  # Shows the change
git diff HEAD      # Shows the change
```

---

### Q15: How do you undo changes in Git?

**Answer:**

**Depends on the state of your changes:**

**1. Unstaged changes (in working directory):**
```bash
# Discard changes to specific file
git restore file.txt

# Discard all changes
git restore .

# Old syntax (still works)
git checkout -- file.txt
```

**2. Staged changes (in staging area):**
```bash
# Unstage file (keep changes)
git restore --staged file.txt

# Old syntax
git reset HEAD file.txt
```

**3. Committed changes:**
```bash
# Undo last commit, keep changes
git reset --soft HEAD~1

# Undo last commit, unstage changes
git reset HEAD~1
git reset --mixed HEAD~1

# Undo last commit, discard all changes
git reset --hard HEAD~1  # ⚠️ DANGEROUS!

# Create new commit that undoes previous
git revert HEAD
```

---

### Q16: How do you delete a file in Git?

**Answer:**

**Method 1: Remove from Git and file system**
```bash
git rm file.txt
git commit -m "Remove file.txt"
```

**Method 2: Stop tracking but keep file**
```bash
# Remove from Git only
git rm --cached file.txt

# Add to .gitignore
echo "file.txt" >> .gitignore

git commit -m "Stop tracking file.txt"
```

**Method 3: Remove directory**
```bash
git rm -r directory/
git commit -m "Remove directory"
```

**What happens:**
```bash
# git rm is equivalent to:
rm file.txt
git add file.txt  # Stages the deletion
```

---

## Troubleshooting Questions

### Q17: What does "detached HEAD" mean and how do you fix it?

**Answer:**

**What it means:**
HEAD points directly to a commit instead of a branch. Changes made won't be on any branch.

**How it happens:**
```bash
# Checkout specific commit
git checkout a3f8d92
# Warning: You are in 'detached HEAD' state...
```

**How to fix:**

**Option 1: Create branch from current state**
```bash
git checkout -b new-branch-name
```

**Option 2: Return to a branch**
```bash
git checkout main
```

**Option 3: Discard changes and return**
```bash
git checkout main
# Changes in detached HEAD are lost
```

**Example scenario:**
```bash
# Accidentally detached
$ git checkout a3f8d92
HEAD is now at a3f8d92

# Made changes and committed
$ git commit -m "Important change"

# Save work by creating branch
$ git checkout -b fix-branch

# Or merge to main
$ git checkout main
$ git merge fix-branch
```

---

### Q18: What do you do when `git push` is rejected?

**Answer:**

**Error message:**
```bash
$ git push origin main
! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs
```

**Cause:**
Remote has commits that your local doesn't have.

**Solution:**

**Method 1: Merge (safe, creates merge commit)**
```bash
git pull origin main
# Resolve conflicts if any
git push origin main
```

**Method 2: Rebase (cleaner history)**
```bash
git pull --rebase origin main
# Resolve conflicts if any
git push origin main
```

**Method 3: Force push (⚠️ dangerous!)**
```bash
# Only use on your own branches
git push --force origin branch-name

# Safer alternative
git push --force-with-lease origin branch-name
```

---

### Q19: How do you resolve merge conflicts?

**Answer:**

**When conflicts occur:**
```bash
$ git merge feature-branch
Auto-merging file.txt
CONFLICT (content): Merge conflict in file.txt
Automatic merge failed; fix conflicts and then commit the result.
```

**Resolution steps:**

**1. Identify conflicted files**
```bash
git status
# Shows: both modified: file.txt
```

**2. Open and edit conflicted file**
```
<<<<<<< HEAD
Current branch content
=======
Merging branch content
>>>>>>> feature-branch
```

**3. Choose resolution:**
- Keep current branch content
- Keep merging branch content
- Combine both
- Write new content

**4. Remove conflict markers**
```
Final resolved content
```

**5. Stage and commit**
```bash
git add file.txt
git commit -m "Resolve merge conflict in file.txt"
```

---

### Q20: What if you committed to the wrong branch?

**Answer:**

**Scenario:** Committed to `main` instead of `feature-branch`

**Solution:**

**Method 1: Move commit to new branch**
```bash
# Create new branch (keeps commit)
git branch feature-branch

# Reset main to before commit
git reset --hard HEAD~1

# Switch to feature branch
git checkout feature-branch
# Commit is now here
```

**Method 2: Move commit to existing branch**
```bash
# On main with wrong commit
git log --oneline  # Note commit hash: a3f8d92

# Switch to correct branch
git checkout feature-branch

# Cherry-pick the commit
git cherry-pick a3f8d92

# Go back and remove from main
git checkout main
git reset --hard HEAD~1
```

---

## Best Practices Questions

### Q21: What should you include in .gitignore?

**Answer:**

**Common items to ignore:**

**1. Dependencies**
```
node_modules/
vendor/
packages/
```

**2. Build outputs**
```
dist/
build/
*.o
*.exe
```

**3. Environment files**
```
.env
.env.local
config.local.json
```

**4. IDE files**
```
.vscode/
.idea/
*.swp
*.swo
.DS_Store
```

**5. Logs**
```
*.log
npm-debug.log*
logs/
```

**6. Temporary files**
```
tmp/
temp/
*.tmp
```

**7. OS files**
```
Thumbs.db
.DS_Store
```

**Example .gitignore:**
```
# Dependencies
node_modules/
package-lock.json

# Environment
.env
.env.local

# Build
dist/
build/
*.min.js

# IDE
.vscode/
.idea/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
```

---

### Q22: What makes a good commit message?

**Answer:**

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Rules:**

**1. Subject line:**
- 50 characters or less
- Imperative mood ("Add" not "Added")
- Capitalize first letter
- No period at end

**2. Body (optional):**
- Wrap at 72 characters
- Explain what and why
- Separate from subject with blank line

**3. Types:**
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Tests
- chore: Maintenance

**Examples:**

```bash
# ✅ Good
git commit -m "Add user authentication endpoint"

git commit -m "Fix null pointer in payment processor

The payment validation was not checking for null
values before processing. Added null check and
appropriate error handling."

git commit -m "feat: Implement JWT token refresh

- Add refresh token endpoint
- Update authentication middleware
- Add token expiration handling

Closes #123"

# ❌ Bad
git commit -m "fixed stuff"
git commit -m "changes"
git commit -m "asdf"
git commit -m "Working now"
```

---

### Q23: How often should you commit?

**Answer:**

**Best practice: Commit early and often**

**Guidelines:**

**1. Logical units of work**
```bash
# ✅ Good: One logical change
git commit -m "Add user model"
git commit -m "Add user validation"
git commit -m "Add user tests"

# ❌ Bad: Everything at once
# ... work for 3 days ...
git commit -m "Add user feature"
```

**2. Working state**
- Code should compile/run
- Tests should pass
- Don't break the build

**3. Before switching context**
```bash
# Before switching branches
git commit -m "WIP: Implementing feature X"

# Or use stash
git stash
```

**4. End of day**
```bash
git commit -m "Complete user authentication UI"
git push origin feature-branch
```

**Benefits of frequent commits:**
- Easier to track changes
- Simpler code review
- Better debugging
- Can revert specific changes
- Clear project evolution

---

### Q24: Should you commit directly to main/master?

**Answer:**

**Short answer: No, use feature branches**

**Why:**

**Problems with committing to main:**
- Can break production code
- Hard to review changes
- Difficult to roll back
- No isolation for experiments
- Team conflicts

**Better approach:**
```bash
# ❌ Bad
git checkout main
# ... make changes ...
git commit -m "Add feature"
git push origin main

# ✅ Good
git checkout -b feature/new-feature
# ... make changes ...
git commit -m "Add feature"
git push origin feature/new-feature
# Create pull request for review
# Merge after approval
```

**Exceptions:**
- Solo projects (still better with branches)
- Hotfixes (create hotfix branch, merge to main)
- Documentation updates (small changes)

**Protected branches:**
```bash
# On GitHub/GitLab, protect main branch:
# - Require pull request reviews
# - Require status checks
# - Require signed commits
# - Restrict who can push
```

---

## Scenario-Based Questions

### Q25: Walk me through your typical Git workflow

**Answer:**

**Daily workflow:**

```bash
# 1. Morning: Start with latest code
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/user-dashboard

# 3. Make changes throughout day
# ... edit files ...
git status  # Check what changed
git diff    # Review changes

# 4. Stage and commit
git add src/dashboard.js
git commit -m "Add dashboard component"

# ... more work ...
git add src/dashboard.css
git commit -m "Style dashboard"

# ... more work ...
git add tests/dashboard.test.js
git commit -m "Add dashboard tests"

# 5. Push at end of day
git push -u origin feature/user-dashboard

# 6. Next day: Continue work
git pull origin feature/user-dashboard
# ... continue ...

# 7. Feature complete: Create PR
# Via GitHub/GitLab interface

# 8. After review and merge
git checkout main
git pull origin main
git branch -d feature/user-dashboard
```

---

### Q26: How do you handle a production bug?

**Answer:**

**Hotfix workflow:**

```bash
# 1. Start from production code
git checkout main
git pull origin main

# 2. Create hotfix branch
git checkout -b hotfix/critical-bug-fix

# 3. Fix the bug
# ... edit files ...
git add fixed-file.js
git commit -m "Fix: Correct null pointer in auth"

# 4. Test thoroughly
# Run tests, manual testing

# 5. Push hotfix
git push origin hotfix/critical-bug-fix

# 6. Create PR for quick review
# Expedited review process

# 7. After approval, merge to main
git checkout main
git merge hotfix/critical-bug-fix

# 8. Tag the fix version
git tag v1.2.3
git push --tags

# 9. Deploy to production
# CI/CD or manual deployment

# 10. Merge to develop (if using Git Flow)
git checkout develop
git merge hotfix/critical-bug-fix

# 11. Clean up
git branch -d hotfix/critical-bug-fix
git push origin --delete hotfix/critical-bug-fix
```

---

### Q27: How would you contribute to an open-source project?

**Answer:**

**Open source contribution workflow:**

```bash
# 1. Fork repository on GitHub (via web interface)

# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/project.git
cd project

# 3. Add upstream remote
git remote add upstream https://github.com/ORIGINAL/project.git

# 4. Create feature branch
git checkout -b fix/documentation-typo

# 5. Make changes
# ... edit files ...
git add README.md
git commit -m "Fix typo in installation instructions"

# 6. Push to your fork
git push origin fix/documentation-typo

# 7. Create pull request
# Via GitHub interface to upstream repository

# 8. Respond to feedback
# Make requested changes
git add file.txt
git commit -m "Address review comments"
git push origin fix/documentation-typo

# 9. Keep fork updated
git fetch upstream
git checkout main
git merge upstream/main
git push origin main

# 10. Rebase feature branch if needed
git checkout fix/documentation-typo
git rebase main
git push --force-with-lease origin fix/documentation-typo
```

---

## Quick Answer Questions

### Q28-Q40: Rapid-fire questions

**Q28: What command initializes a Git repository?**  
**A:** `git init`

**Q29: How do you stage all files?**  
**A:** `git add .` or `git add -A`

**Q30: How do you unstage a file?**  
**A:** `git restore --staged file.txt` or `git reset HEAD file.txt`

**Q31: How do you view commit history in one line?**  
**A:** `git log --oneline`

**Q32: How do you create a new branch?**  
**A:** `git branch branch-name` or `git checkout -b branch-name`

**Q33: How do you switch branches?**  
**A:** `git checkout branch-name` or `git switch branch-name`

**Q34: How do you clone a repository?**  
**A:** `git clone <url>`

**Q35: How do you view current branch?**  
**A:** `git branch` (current marked with *) or `git status`

**Q36: How do you delete a branch?**  
**A:** `git branch -d branch-name` (merged) or `git branch -D branch-name` (force)

**Q37: How do you see remote repositories?**  
**A:** `git remote -v`

**Q38: How do you fetch changes from remote?**  
**A:** `git fetch` (download only) or `git pull` (download and merge)

**Q39: How do you push to remote?**  
**A:** `git push origin branch-name`

**Q40: How do you see differences between commits?**  
**A:** `git diff commit1 commit2`

---

## Interview Tips

### Preparation Tips

**1. Practice common commands**
```bash
# Create test repository and practice
mkdir git-practice
cd git-practice
git init
# Practice all basic commands
```

**2. Understand concepts, not just commands**
- Why staging area exists
- How branches work internally
- What makes Git distributed

**3. Know the terminology**
- Repository, commit, branch, remote, HEAD
- Working directory, staging area, .git directory
- Fast-forward, merge, rebase

**4. Be ready with examples**
- Real projects you've worked on
- Conflicts you've resolved
- Workflows you've used

**5. Admit what you don't know**
- Better to say "I don't know" than make up answers
- Show willingness to learn

### During Interview

**Do:**
- ✅ Explain your thought process
- ✅ Use diagrams if helpful
- ✅ Give real examples
- ✅ Ask clarifying questions
- ✅ Mention best practices

**Don't:**
- ❌ Memorize commands without understanding
- ❌ Pretend to know everything
- ❌ Skip explanation and just give commands
- ❌ Ignore the "why" behind things

### Common Follow-up Questions

**After answering "What is Git?":**
- How is it different from SVN?
- Why distributed vs centralized?
- What problems does it solve?

**After explaining branching:**
- How do you handle merge conflicts?
- What's your branching strategy?
- When do you create branches?

**After discussing commits:**
- How do you write good commit messages?
- How often do you commit?
- What should be in a commit?

---

## Summary Checklist

Before your interview, make sure you can:

✅ **Explain conceptually:**
- [ ] What Git is and why we use it
- [ ] The three states (modified, staged, committed)
- [ ] How branches work
- [ ] The difference between Git and GitHub

✅ **Demonstrate practically:**
- [ ] Initialize a repository
- [ ] Stage and commit changes
- [ ] Create and merge branches
- [ ] Resolve conflicts
- [ ] Push/pull from remote

✅ **Discuss workflows:**
- [ ] Your daily development workflow
- [ ] How you handle bugs
- [ ] Team collaboration strategies
- [ ] When and why to branch

✅ **Troubleshoot:**
- [ ] Rejected pushes
- [ ] Merge conflicts
- [ ] Detached HEAD
- [ ] Wrong branch commits

---

**Previous:** [← Remote Repositories](05-remote-repositories.md) | **Next:** [Git Practice Labs →](../../01-git/git-practice/)

---

*Practice these questions, understand the concepts, and you'll be well-prepared for Git interview questions!*
