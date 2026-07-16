# PowerShell Script to Create All Git Content Files
# Run: .\CREATE_ALL_FILES.ps1

Write-Host "Creating all Git content files..." -ForegroundColor Cyan

# Helper function
function Create-GitFile {
    param($Path, $Content)
    $Content | Out-File -FilePath $Path -Encoding utf8
    if (Test-Path $Path) {
        $size = (Get-Item $Path).Length
        Write-Host "✅ Created: $Path ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed: $Path" -ForegroundColor Red
    }
}

# Intermediate Files
$files = @{
    "intermediate/06-branching-merging.md" = @"
# Branching and Merging
Master Git branching and merging for parallel development.

## Branch Basics
Branches allow independent development lines.

### Creating Branches
``````bash
git branch feature-name
git checkout -b feature-name
git switch -c feature-name
``````

### Switching Branches
``````bash
git checkout branch-name
git switch branch-name
``````

### Listing Branches
``````bash
git branch
git branch -a
git branch -v
``````

### Deleting Branches
``````bash
git branch -d branch-name
git branch -D branch-name
``````

## Merging
Integrate changes from one branch to another.

### Fast-Forward Merge
``````bash
git checkout main
git merge feature-branch
``````

### Three-Way Merge
``````bash
git merge --no-ff feature-branch
``````

### Merge Conflicts
``````bash
# When conflict occurs
git status
# Edit conflicted files
git add resolved-file.txt
git commit
``````

## Best Practices
1. Keep branches short-lived
2. Merge frequently
3. Delete merged branches
4. Use descriptive names

**Previous:** [Remote Repositories](../basics/05-remote-repositories.md) | **Next:** [Branching Strategies →](07-branching-strategies.md)
"@

    "intermediate/07-branching-strategies.md" = @"
# Git Branching Strategies
Learn different branching workflows for team collaboration.

## GitFlow
Feature branches, develop, main, hotfix, release branches.

``````bash
# Start feature
git checkout -b feature/new-feature develop

# Finish feature
git checkout develop
git merge feature/new-feature
``````

## GitHub Flow
Simplified: main branch + feature branches.

``````bash
git checkout -b feature-name
# Work and commit
git push origin feature-name
# Create PR
``````

## Trunk-Based Development
Short-lived branches, frequent integration.

``````bash
git checkout -b quick-feature
# Small changes
git checkout main
git merge quick-feature
``````

## Best Practices
- Choose strategy based on team size
- Document your workflow
- Automate with CI/CD

**Previous:** [← Branching and Merging](06-branching-merging.md) | **Next:** [Resolving Conflicts →](08-resolving-conflicts.md)
"@

    "intermediate/08-resolving-conflicts.md" = @"
# Resolving Merge Conflicts
Handle conflicts when branches diverge.

## Understanding Conflicts
Conflicts occur when same lines are changed in different branches.

## Conflict Markers
``````
<<<<<<< HEAD
Current branch changes
=======
Merging branch changes
>>>>>>> feature-branch
``````

## Resolution Steps
``````bash
# 1. Identify conflicts
git status

# 2. Open and edit files
# Remove markers, keep desired changes

# 3. Stage resolved files
git add resolved-file.txt

# 4. Complete merge
git commit
``````

## Prevention
- Pull frequently
- Communicate with team
- Keep changes small

**Previous:** [← Branching Strategies](07-branching-strategies.md) | **Next:** [Rebase vs Merge →](09-rebase-vs-merge.md)
"@

    "intermediate/09-rebase-vs-merge.md" = @"
# Git Rebase vs Merge
Understand when to rebase and when to merge.

## Merge
Creates a merge commit, preserves history.

``````bash
git checkout main
git merge feature-branch
``````

Pros: Safe, preserves context
Cons: Can clutter history

## Rebase
Replays commits on top of another branch.

``````bash
git checkout feature-branch
git rebase main
``````

Pros: Clean linear history
Cons: Rewrites history

## When to Use
- **Merge**: For shared branches, preserving history
- **Rebase**: For local branches, cleaning up

## Golden Rule
Never rebase public/shared branches!

**Previous:** [← Resolving Conflicts](08-resolving-conflicts.md) | **Next:** [Stash and Cherry-pick →](10-stash-cherry-pick.md)
"@

    "intermediate/10-stash-cherry-pick.md" = @"
# Git Stash and Cherry-Pick
Temporarily save work and selectively apply commits.

## Git Stash
Save uncommitted changes temporarily.

``````bash
# Stash changes
git stash

# List stashes
git stash list

# Apply stash
git stash apply
git stash pop

# Stash with message
git stash save 'WIP: feature'

# Drop stash
git stash drop
``````

## Git Cherry-Pick
Apply specific commits from another branch.

``````bash
# Pick single commit
git cherry-pick commit-hash

# Pick multiple commits
git cherry-pick hash1 hash2

# Cherry-pick without commit
git cherry-pick -n commit-hash
``````

## Use Cases
- Moving commits between branches
- Applying hotfixes
- Selective backporting

**Previous:** [← Rebase vs Merge](09-rebase-vs-merge.md) | **Next:** [Tags and Releases →](11-tags-releases.md)
"@

    "intermediate/11-tags-releases.md" = @"
# Git Tags and Releases
Mark important points in history with tags.

## Tag Types

### Lightweight Tags
``````bash
git tag v1.0.0
``````

### Annotated Tags
``````bash
git tag -a v1.0.0 -m 'Release version 1.0.0'
``````

## Tag Operations

``````bash
# List tags
git tag
git tag -l 'v1.*'

# Show tag info
git show v1.0.0

# Push tags
git push origin v1.0.0
git push origin --tags

# Delete tag
git tag -d v1.0.0
git push origin --delete v1.0.0
``````

## Semantic Versioning
MAJOR.MINOR.PATCH (1.2.3)
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

## Best Practices
- Use annotated tags for releases
- Follow semantic versioning
- Tag after successful deployment

**Previous:** [← Stash and Cherry-Pick](10-stash-cherry-pick.md) | **Next:** [Pull Requests →](12-pull-requests.md)
"@

    "intermediate/12-pull-requests.md" = @"
# Pull Requests and Code Review
Collaborate effectively with pull requests.

## Creating Pull Requests

``````bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m 'Add new feature'

# 3. Push to remote
git push origin feature/new-feature

# 4. Create PR on GitHub/GitLab
``````

## PR Best Practices
1. Keep PRs small and focused
2. Write clear descriptions
3. Link to issues
4. Request specific reviewers
5. Respond to feedback promptly

## Code Review Process
- Review code, not people
- Ask questions, don't demand changes
- Provide constructive feedback
- Approve or request changes

## After Merge
``````bash
git checkout main
git pull origin main
git branch -d feature/new-feature
``````

**Previous:** [← Tags and Releases](11-tags-releases.md) | **Next:** [Interview Questions →](interview-questions-intermediate.md)
"@

    "intermediate/interview-questions-intermediate.md" = @"
# Git Interview Questions - Intermediate Level

## Branching Questions

### Q1: What is a Git branch?
**Answer:** A lightweight movable pointer to a commit that allows parallel development without affecting the main codebase.

### Q2: Difference between merge and rebase?
**Answer:** Merge creates a merge commit preserving history. Rebase replays commits creating linear history. Never rebase shared branches.

### Q3: How to resolve merge conflicts?
**Answer:** 
1. git status to identify conflicts
2. Edit files removing conflict markers
3. git add resolved files
4. git commit to complete merge

## Workflow Questions

### Q4: Explain GitFlow workflow
**Answer:** Uses main (production), develop (integration), feature/* (new features), hotfix/* (emergency fixes), and release/* (release prep) branches.

### Q5: What is cherry-pick?
**Answer:** Applies specific commits from one branch to another without merging entire branch.

### Q6: When to use git stash?
**Answer:** Temporarily save uncommitted changes when switching branches or pulling updates.

## Tag Questions

### Q7: Difference between lightweight and annotated tags?
**Answer:** Lightweight is just a pointer. Annotated includes tagger name, email, date, and message - recommended for releases.

### Q8: How to tag a specific commit?
**Answer:** \`git tag -a v1.0.0 commit-hash -m 'message'\`

## Pull Request Questions

### Q9: What makes a good PR?
**Answer:** Small focused changes, clear description, linked issues, passing tests, responsive to feedback.

### Q10: How to update PR with new commits?
**Answer:** Make changes locally, commit, and push to same branch. PR updates automatically.

**Previous:** [← Pull Requests](12-pull-requests.md) | **Next:** [Git Internals →](../advanced/13-git-internals.md)
"@
}

# Create all files
foreach ($file in $files.Keys) {
    $fullPath = $file
    $dir = Split-Path $fullPath -Parent
    if ($dir) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Create-GitFile -Path $fullPath -Content $files[$file]
}

Write-Host "`nIntermediate files created!" -ForegroundColor Green
Write-Host "Total: $($files.Count) files" -ForegroundColor Cyan
