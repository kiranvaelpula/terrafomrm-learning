# Git Interview Questions - Advanced Level

### Q1: Explain Git internals
**Answer:** Git stores data as snapshots using four object types: blobs (file contents), trees (directory structure), commits (snapshots with metadata), and tags (named references). All identified by SHA-1 hashes.

### Q2: How does Git garbage collection work?
**Answer:** git gc removes unreachable objects, compresses files, and optimizes repository. Runs automatically or manually via \git gc\.

### Q3: What is Git reflog?
**Answer:** Local history of HEAD changes. Used to recover lost commits, deleted branches, or undo operations.

### Q4: Explain Git hooks
**Answer:** Scripts that run automatically on Git events (pre-commit, pre-push, etc.). Used for testing, linting, commit message validation.

### Q5: How to handle large files in Git?
**Answer:** Use Git LFS (Large File Storage) to store large files externally while keeping repository lightweight.

### Q6: Monorepo vs multi-repo?
**Answer:** Monorepo: single repo for multiple projects (atomic changes, simplified deps). Multi-repo: separate repos (smaller size, independent deploys).

### Q7: How to sign commits?
**Answer:** Use GPG keys. Configure with \git config --global commit.gpgsign true\. Sign with \git commit -S\.

### Q8: Explain Git bisect
**Answer:** Binary search to find commit that introduced bug. Mark commits as good/bad until bug source identified.

### Q9: How to recover deleted branch?
**Answer:** Use \git reflog\ to find commit, then \git branch branch-name commit-hash\.

### Q10: Git security best practices?
**Answer:** Never commit secrets, use .gitignore, sign commits with GPG, enable branch protection, audit repository access, scan for secrets.

**Previous:** [â† Troubleshooting](20-troubleshooting.md) | **Next:** [Labs â†’](../git-practice/)
