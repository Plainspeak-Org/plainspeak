# Git Plugin

The Git Plugin provides seamless integration with Git version control, allowing you to manage repositories, branches, and changes through natural language commands.

## Overview

Version control is essential for modern software development. The Git Plugin gives you the power to initialize repositories, clone projects, commit changes, and work with branches using simple, intuitive commands, all without remembering complex Git syntax.

## Prerequisites

- Git must be installed on your system (version 2.0.0 or higher)
- For remote operations, appropriate network access and authentication must be configured

## Verbs

| Verb | Description |
|------|-------------|
| `git-init` | Initialize a new Git repository |
| `git-clone` | Clone a Git repository |
| `git-status` | Show working tree status |
| `git-add` | Add files to Git staging area |
| `git-commit` | Record changes to the repository |
| `git-push` | Update remote repository |
| `git-pull` | Fetch and merge changes from remote |
| `git-branch` | List, create, or delete branches |
| `git-checkout` | Switch or create branches |
| `git-merge` | Join two or more development histories together |
| `git-log` | Show commit logs |

## Usage Examples

### Repository Setup

```
# Initialize a new repository
create a new git repository here
git init

# Clone a repository
clone the repository from https://github.com/user/repo
git clone https://github.com/user/repo

# Clone with a specific path
clone https://github.com/user/repo to my-project
git clone https://github.com/user/repo my-project

# Clone with depth limit (shallow clone)
clone the TensorFlow repository with depth 1
git clone --depth 1 https://github.com/tensorflow/tensorflow
```

### Checking Status

```
# Show repository status
show git status
git status

# Show compact status
show git status in short format
git status --short
```

### Staging Changes

```
# Stage all changes
add all files to git
git add .

# Stage specific files
add src/main.py to git
git add src/main.py

# Stage only modified files (not new files)
add modified files to git
git add -u
```

### Committing Changes

```
# Commit with message
commit changes with message "Fix bug in parser"
git commit -m "Fix bug in parser"

# Amend previous commit
amend the last commit with message "Fix typo in documentation"
git commit --amend -m "Fix typo in documentation"
```

### Working with Remotes

```
# Push to default remote
push changes to origin
git push origin

# Push to specific branch
push changes to the main branch
git push origin main

# Force push (use cautiously)
force push to origin
git push origin --force

# Pull from remote
pull latest changes
git pull

# Pull from specific branch
pull changes from origin develop
git pull origin develop
```

### Branch Management

```
# List branches
show all branches
git branch

# Create a new branch
create a new branch called feature
git branch feature

# Delete a branch
delete the old-feature branch
git branch --delete old-feature

# Switch to a branch
switch to master branch
git checkout master

# Create and switch to a new branch
create and checkout new-feature branch
git checkout -b new-feature
```

### Merging

```
# Merge a branch
merge feature branch into current branch
git merge feature

# Merge with no fast-forward
merge development branch with no fast forward
git merge development --no-ff
```

### Viewing History

```
# Show commit history
show commit history
git log

# Show simplified history
show commit log in one line format
git log --oneline

# Limit history
show last 5 commits
git log -n 5
```

## Advanced Usage

### Working with Stashes

```
# Stash changes
save my changes for later
git stash

# Apply stashed changes
apply my stashed changes
git stash apply

# List stashes
show all stashes
git stash list
```

### Working with Tags

```
# Create a tag
tag this commit as v1.0.0
git tag v1.0.0

# List tags
show all tags
git tag

# Push tags
push tags to origin
git push --tags
```

### Interactive Operations

```
# Interactive rebase
start interactive rebase for the last 3 commits
git rebase -i HEAD~3

# Interactive add
interactively choose what to stage
git add -i
```

## Configuration

The Git Plugin can be configured in your PlainSpeak configuration file:

```toml
[plugins.git]
# Default remote repository
default_remote = "origin"

# Default branch
default_branch = "main"

# Default commit message when none provided
default_commit_message = "Update files"

# SSH key location
ssh_key = "~/.ssh/id_rsa"
```

## Best Practices

1. **Commit frequently**: Make small, focused commits that address a single issue or feature.
2. **Write meaningful commit messages**: Use clear, descriptive commit messages that explain what changed and why.
3. **Pull before pushing**: Always pull the latest changes before pushing to avoid conflicts.
4. **Use branches for features**: Create a new branch for each feature or bug fix to isolate changes.
5. **Be careful with force operations**: Force pushing or force checkout can overwrite history; use with caution.

## Troubleshooting

### Common Issues

1. **Authentication failures**: Ensure your SSH keys or credentials are properly set up for remote operations.
2. **Merge conflicts**: When Git can't automatically merge changes, you'll need to resolve conflicts manually.
3. **Detached HEAD state**: This occurs when you check out a specific commit instead of a branch. Create a branch if you want to save changes.
4. **Large repository issues**: Very large repositories may be slow to clone; consider using `--depth` for shallow clones.

### Error Messages

| Error Message | Possible Solution |
|---------------|-------------------|
| "not a git repository" | Ensure you're in a Git repository, or initialize one with `git init` |
| "Permission denied" | Check that you have the correct access credentials for the remote repository |
| "Merge conflict" | You'll need to manually resolve conflicts, then complete the merge |
| "Changes not staged for commit" | Stage your changes with `git add` before committing |
| "Updates were rejected" | Pull latest changes first, resolve any conflicts, then push again |

### Getting Help

For more detailed information on Git commands:

```
show help for git commit
git commit --help
```

## Examples in Context

### Complete Workflow Example

```
# Start a new project
create a new git repository here
git init

# Create some files and make initial commit
add all files to git
git commit -m "Initial commit"

# Create a feature branch
create and checkout feature-login branch
git checkout -b feature-login

# Make changes and commit
add all changes to git
git commit -m "Implement login functionality"

# Switch back to main branch
switch to main branch
git checkout main

# Merge the feature
merge feature-login branch
git merge feature-login

# Push to remote
push changes to origin
git push origin
```

### Collaborative Workflow

```
# Clone a repository
clone https://github.com/team/project
git clone https://github.com/team/project

# Create a feature branch
create and checkout my-feature branch
git checkout -b my-feature

# Make changes and commit
add all files to git
git commit -m "Implement my feature"

# Push branch to remote
push my-feature branch to origin
git push origin my-feature

# After pull request is approved, update main
switch to main branch
git checkout main

# Get latest changes
pull from origin
git pull origin

# Clean up feature branch
delete my-feature branch
git branch --delete my-feature
``` 