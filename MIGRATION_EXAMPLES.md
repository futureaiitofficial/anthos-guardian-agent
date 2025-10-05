# Migration Usage Examples

This document provides practical examples of using the repository migration tools.

## Table of Contents
1. [Automated Migration Example](#automated-migration-example)
2. [Manual Migration Example](#manual-migration-example)
3. [Verification Examples](#verification-examples)
4. [Common Scenarios](#common-scenarios)
5. [Troubleshooting Examples](#troubleshooting-examples)

---

## Automated Migration Example

### Using the Migration Script

The easiest way to migrate the repository is using the automated script:

```bash
# Step 1: Download or clone this repository
git clone https://github.com/futureaiitofficial/anthos-guardian-agent.git
cd anthos-guardian-agent

# Step 2: Run the migration script
./migrate-to-bank-guardian-ai.sh
```

### Expected Output

```
==========================================
Bank Guardian AI - Repository Migration Script
==========================================

✓ Git is installed

==========================================
Step 1: Cloning source repository
==========================================

Cloning from: https://github.com/futureaiitofficial/anthos-guardian-agent.git
Cloning into 'bank-guardian-ai-migration-temp'...
✓ Source repository cloned successfully

==========================================
Step 2: Removing git history
==========================================

✓ Git history removed

==========================================
Step 3: Initializing new git repository
==========================================

Initialized empty Git repository in /path/to/bank-guardian-ai-migration-temp/.git/
✓ New git repository initialized

==========================================
Step 4: Checking git configuration
==========================================

✓ Using existing git configuration: Your Name <your.email@example.com>

==========================================
Step 5: Adding remote repository
==========================================

Target repository: https://github.com/lahari17/bank-guardian-ai.git
✓ Remote repository added

==========================================
Step 6: Staging all files
==========================================

✓ Staged 250 files

==========================================
Step 7: Creating initial commit
==========================================

✓ Initial commit created

==========================================
Migration Summary
==========================================

Repository: /path/to/bank-guardian-ai-migration-temp
Remote URL: https://github.com/lahari17/bank-guardian-ai.git
Branch: main
Commit count: 1
Latest commit: a1b2c3d Initial commit: Bank Guardian AI...

==========================================
Step 9: Ready to push
==========================================

⚠ This will push to: https://github.com/lahari17/bank-guardian-ai.git
⚠ This operation will overwrite the remote repository if it already has content!
Do you want to proceed with pushing? (y/n) y

Pushing to remote repository...
✓ Repository pushed successfully

==========================================
Migration Complete!
==========================================

✓ Repository successfully migrated to: https://github.com/lahari17/bank-guardian-ai.git

Next steps:
1. Visit: https://github.com/lahari17/bank-guardian-ai
2. Verify all files are present
3. Check that only one commit exists
4. Update repository settings (branch protection, secrets, etc.)

The migrated repository is located at: /path/to/bank-guardian-ai-migration-temp
You can safely delete this directory after verification:
  cd .. && rm -rf bank-guardian-ai-migration-temp

==========================================
Thank you for using Bank Guardian AI!
==========================================
```

---

## Manual Migration Example

### Step-by-Step Manual Process

```bash
# Step 1: Clone the source repository
git clone https://github.com/futureaiitofficial/anthos-guardian-agent.git
cd anthos-guardian-agent

# Step 2: Verify what you have
ls -la
# You should see all project files

# Step 3: Check current git status
git log --oneline
# You'll see multiple commits from the history

# Step 4: Remove git history
rm -rf .git

# Step 5: Initialize a fresh repository
git init
# Output: Initialized empty Git repository in .git/

# Step 6: Configure git (if needed)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Step 7: Add the new remote
git remote add origin https://github.com/lahari17/bank-guardian-ai.git

# Step 8: Verify remote
git remote -v
# Output:
# origin  https://github.com/lahari17/bank-guardian-ai.git (fetch)
# origin  https://github.com/lahari17/bank-guardian-ai.git (push)

# Step 9: Stage all files
git add .

# Step 10: Check what will be committed
git status
# Shows all files as "new file"

# Step 11: Create initial commit
git commit -m "Initial commit: Bank Guardian AI - AI-powered fraud detection system for Bank of Anthos

This repository contains:
- Financial Guardian: AI-powered fraud detection
- Ops Guardian: Infrastructure optimization
- Explainer Agent: Natural language explanations
- Guardian Dashboard: Unified monitoring interface
- Bank of Anthos: Base banking application

Technologies: Python, Java, Kubernetes, Google Gemini AI, PostgreSQL"

# Step 12: Verify commit
git log --oneline
# Output: a1b2c3d (HEAD -> master) Initial commit: Bank Guardian AI...
# Only one commit!

# Step 13: Switch to main branch
git branch -M main

# Step 14: Push to remote
git push -u origin main
```

---

## Verification Examples

### Verify Clean History

```bash
# After migration, check commit count
cd bank-guardian-ai-migration-temp  # or your target directory
git log --oneline

# Expected output: Only ONE commit
# a1b2c3d Initial commit: Bank Guardian AI - AI-powered fraud detection system for Bank of Anthos

# Check detailed history
git log

# Expected output:
# commit a1b2c3d4e5f6g7h8i9j0
# Author: Your Name <your.email@example.com>
# Date:   Mon Oct 5 12:00:00 2024 +0000
#
#     Initial commit: Bank Guardian AI - AI-powered fraud detection system for Bank of Anthos
```

### Verify All Files Present

```bash
# List all directories
ls -la

# Expected output:
# drwxr-xr-x  docs/
# drwxr-xr-x  extras/
# drwxr-xr-x  iac/
# drwxr-xr-x  kubernetes-manifests/
# drwxr-xr-x  src/
# -rw-r--r--  .gitignore
# -rw-r--r--  README.md
# -rw-r--r--  Bank_Guardian_AI_Project.md
# ... and more files

# Check Guardian AI services
ls -la src/
# Expected output should include:
# drwxr-xr-x  financial-guardian/
# drwxr-xr-x  ops-guardian/
# drwxr-xr-x  explainer-agent/
# drwxr-xr-x  guardian-dashboard/
# ... and more services

# Count total files
find . -type f | wc -l
# Should show similar count to original repo
```

### Verify Remote Configuration

```bash
# Check remote URL
git remote get-url origin
# Expected: https://github.com/lahari17/bank-guardian-ai.git

# Check all remotes
git remote -v
# Expected:
# origin  https://github.com/lahari17/bank-guardian-ai.git (fetch)
# origin  https://github.com/lahari17/bank-guardian-ai.git (push)

# Verify push worked
git branch -a
# Expected:
# * main
#   remotes/origin/main
```

---

## Common Scenarios

### Scenario 1: Migrating with SSH Instead of HTTPS

```bash
# Run script normally until remote setup
./migrate-to-bank-guardian-ai.sh

# Or manually change remote after migration
git remote set-url origin git@github.com:lahari17/bank-guardian-ai.git

# Then push
git push -u origin main
```

### Scenario 2: Migrating to a Different Repository Name

Edit the migration script before running:

```bash
# Open the script
nano migrate-to-bank-guardian-ai.sh

# Change this line:
TARGET_REPO="https://github.com/lahari17/YOUR-NEW-REPO-NAME.git"

# Save and run
./migrate-to-bank-guardian-ai.sh
```

### Scenario 3: Adding Custom Initial Commit Message

Edit the script:

```bash
# Open the script
nano migrate-to-bank-guardian-ai.sh

# Change this line to your preferred message:
COMMIT_MESSAGE="Your custom initial commit message here"

# Save and run
./migrate-to-bank-guardian-ai.sh
```

### Scenario 4: Dry Run (Without Pushing)

```bash
# Run the script
./migrate-to-bank-guardian-ai.sh

# When prompted "Do you want to proceed with pushing?", answer: n

# The repository is ready but not pushed
# You can inspect it in: bank-guardian-ai-migration-temp/

# To push later:
cd bank-guardian-ai-migration-temp
git push -u origin main
```

---

## Troubleshooting Examples

### Issue: "Permission Denied" Error

```bash
# Error message:
# remote: Permission to lahari17/bank-guardian-ai.git denied to username.

# Solution 1: Configure SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"
cat ~/.ssh/id_ed25519.pub
# Add the SSH key to GitHub

# Change remote to SSH
git remote set-url origin git@github.com:lahari17/bank-guardian-ai.git
git push -u origin main

# Solution 2: Use GitHub token
git remote set-url origin https://YOUR-TOKEN@github.com/lahari17/bank-guardian-ai.git
git push -u origin main
```

### Issue: "Repository Not Empty" Error

```bash
# Error message:
# ! [rejected]        main -> main (non-fast-forward)

# Solution: Force push (USE WITH CAUTION - this will overwrite remote content)
git push -u origin main --force

# Or, if you want to preserve remote content:
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Issue: Migration Script Already Exists

```bash
# Error: bank-guardian-ai-migration-temp already exists

# Solution 1: Remove and retry
rm -rf bank-guardian-ai-migration-temp
./migrate-to-bank-guardian-ai.sh

# Solution 2: Use existing directory
cd bank-guardian-ai-migration-temp
git push -u origin main
```

### Issue: Large Files Warning

```bash
# Warning: Large files detected

# Solution: Remove large files before committing
cd bank-guardian-ai-migration-temp
rm -rf node_modules dist build target

# Recommit
git reset HEAD~1
git add .
git commit -m "Initial commit: Bank Guardian AI"
git push -u origin main --force
```

---

## Post-Migration Verification Checklist

After migration, verify the following:

```bash
# 1. Check you're in the right directory
pwd
# Expected: /path/to/bank-guardian-ai-migration-temp

# 2. Check remote
git remote -v
# Expected: origin points to lahari17/bank-guardian-ai.git

# 3. Check commit history
git log --oneline
# Expected: Only ONE commit

# 4. Check branch
git branch
# Expected: * main

# 5. Check file count
find . -type f -not -path "./.git/*" | wc -l
# Expected: Similar to original repo

# 6. Visit GitHub
# Open: https://github.com/lahari17/bank-guardian-ai
# Verify: All files present, only one commit

# 7. Test clone
cd /tmp
git clone https://github.com/lahari17/bank-guardian-ai.git test-clone
cd test-clone
git log --oneline
# Expected: Only one commit
```

---

## Next Steps After Migration

1. **Configure GitHub Repository Settings:**
   ```
   - Go to Settings → Branches
   - Add branch protection rule for main branch
   - Enable "Require pull request reviews"
   - Enable "Require status checks to pass"
   ```

2. **Add GitHub Secrets:**
   ```
   - Go to Settings → Secrets and variables → Actions
   - Add: GEMINI_API_KEY
   - Add: GCP_PROJECT_ID (if using GCP)
   - Add other required secrets
   ```

3. **Update README with New URLs:**
   ```bash
   # Clone your new repository
   git clone https://github.com/lahari17/bank-guardian-ai.git
   cd bank-guardian-ai
   
   # Update any references to old repository
   find . -type f -name "*.md" -exec sed -i 's/futureaiitofficial\/anthos-guardian-agent/lahari17\/bank-guardian-ai/g' {} +
   
   # Commit changes
   git add .
   git commit -m "Update repository URLs"
   git push origin main
   ```

4. **Test Deployment:**
   Follow the deployment guide to ensure everything works in the new repository.

---

## Summary

This migration process ensures:
- ✅ **Clean History**: Only one initial commit
- ✅ **All Files**: Complete repository content preserved
- ✅ **No History**: Previous commits are not carried over
- ✅ **Fresh Start**: New repository ready for development

For more information, see:
- [MIGRATION_QUICK_START.md](./MIGRATION_QUICK_START.md) - Quick reference
- [REPOSITORY_MIGRATION_GUIDE.md](./REPOSITORY_MIGRATION_GUIDE.md) - Comprehensive guide

