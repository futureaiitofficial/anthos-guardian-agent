# Repository Migration Guide

## Overview

This guide explains how to migrate the `anthos-guardian-agent` repository to `bank-guardian-ai` with a clean commit history.

## Prerequisites

- Git installed on your local machine
- Access to both GitHub repositories:
  - Source: `https://github.com/futureaiitofficial/anthos-guardian-agent.git`
  - Target: `https://github.com/lahari17/bank-guardian-ai.git`
- GitHub credentials configured for pushing to the target repository

## Migration Methods

### Method 1: Automated Migration (Recommended)

Use the provided migration script:

```bash
# Run the migration script
./migrate-to-bank-guardian-ai.sh
```

The script will:
1. Clone the source repository
2. Remove the existing git history
3. Create a fresh git repository
4. Add and commit all files with a clean history
5. Push to the target repository

### Method 2: Manual Migration

Follow these steps to manually migrate the repository:

#### Step 1: Clone the Source Repository

```bash
# Clone the anthos-guardian-agent repository
git clone https://github.com/futureaiitofficial/anthos-guardian-agent.git
cd anthos-guardian-agent
```

#### Step 2: Remove Git History

```bash
# Remove the existing .git directory to erase all commit history
rm -rf .git
```

#### Step 3: Initialize New Git Repository

```bash
# Initialize a new git repository with a clean history
git init
```

#### Step 4: Configure Git

```bash
# Set your git user information (if not already configured)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

#### Step 5: Add Remote Repository

```bash
# Add the bank-guardian-ai repository as remote
git remote add origin https://github.com/lahari17/bank-guardian-ai.git
```

#### Step 6: Stage All Files

```bash
# Add all files to staging
git add .
```

#### Step 7: Create Initial Commit

```bash
# Create a clean initial commit
git commit -m "Initial commit: Bank Guardian AI - AI-powered fraud detection system for Bank of Anthos"
```

#### Step 8: Push to Remote Repository

```bash
# Push to the main branch
git branch -M main
git push -u origin main
```

## Verification Steps

After migration, verify the repository:

1. **Check Remote URL:**
   ```bash
   git remote -v
   ```
   Expected output:
   ```
   origin  https://github.com/lahari17/bank-guardian-ai.git (fetch)
   origin  https://github.com/lahari17/bank-guardian-ai.git (push)
   ```

2. **Check Commit History:**
   ```bash
   git log --oneline
   ```
   You should see only one commit (the initial commit).

3. **Verify All Files:**
   ```bash
   ls -la
   ```
   Ensure all files from the source repository are present.

4. **Visit GitHub:**
   Navigate to `https://github.com/lahari17/bank-guardian-ai` and verify:
   - All files are present
   - Only one commit exists in the history
   - README and documentation are accessible

## What Gets Migrated

The following components will be migrated:

### Guardian AI Services
- **Financial Guardian** - AI-powered fraud detection service
- **Ops Guardian** - Infrastructure optimization and scaling
- **Explainer Agent** - User-friendly explanations for AI decisions
- **Guardian Dashboard** - Unified monitoring and control interface

### Bank of Anthos Base Application
- All microservices (frontend, ledger, accounts, etc.)
- Kubernetes manifests
- Documentation
- Infrastructure as Code (Terraform)
- CI/CD configurations

### Documentation
- Deployment guides
- API documentation
- Development guides
- Architecture diagrams

## Post-Migration Tasks

After successful migration:

1. **Update Documentation:**
   - Update any references to the old repository URL
   - Update clone commands in README files
   - Update deployment guides

2. **Configure GitHub Settings:**
   - Set up branch protection rules
   - Configure CI/CD pipelines
   - Set up secrets for deployments (GEMINI_API_KEY, etc.)

3. **Update Team Access:**
   - Add team members as collaborators
   - Configure access permissions

4. **Test Deployments:**
   - Follow the deployment guide to ensure everything works
   - Test Guardian AI services
   - Verify Bank of Anthos functionality

## Troubleshooting

### Error: Remote already exists
```bash
git remote remove origin
git remote add origin https://github.com/lahari17/bank-guardian-ai.git
```

### Error: Permission denied
Ensure you have push access to the target repository and your GitHub credentials are configured:
```bash
# Use SSH instead of HTTPS
git remote set-url origin git@github.com:lahari17/bank-guardian-ai.git
```

### Large Files Warning
If you encounter issues with large files:
```bash
# Remove unnecessary build artifacts or large files
rm -rf node_modules dist build target
git add .
git commit --amend --no-edit
```

## Important Notes

- **No History Preservation:** This migration creates a clean slate with no commit history from the source repository.
- **Attribution:** Consider adding a note in the README acknowledging the original Bank of Anthos project and the Guardian AI enhancements.
- **Backup:** Keep a backup of the original repository until you've verified the migration is successful.

## Support

For issues or questions:
- Review the troubleshooting section above
- Check GitHub documentation on repository management
- Contact the repository administrator

## Migration Checklist

- [ ] Clone source repository
- [ ] Remove git history
- [ ] Initialize new git repository
- [ ] Add remote repository
- [ ] Stage all files
- [ ] Create initial commit
- [ ] Push to remote
- [ ] Verify on GitHub
- [ ] Update documentation references
- [ ] Configure GitHub settings
- [ ] Test deployments
- [ ] Archive or document source repository reference

