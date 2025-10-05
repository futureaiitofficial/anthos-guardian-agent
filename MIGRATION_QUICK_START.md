# Quick Migration Reference

## Migrate to bank-guardian-ai Repository

This repository needs to be migrated to `https://github.com/lahari17/bank-guardian-ai.git` with a clean commit history.

### Quick Start (Automated)

```bash
# Run the migration script
./migrate-to-bank-guardian-ai.sh
```

### Manual Steps

```bash
# 1. Clone this repo
git clone https://github.com/futureaiitofficial/anthos-guardian-agent.git
cd anthos-guardian-agent

# 2. Remove git history
rm -rf .git

# 3. Initialize new repo
git init

# 4. Add remote
git remote add origin https://github.com/lahari17/bank-guardian-ai.git

# 5. Commit and push
git add .
git commit -m "Initial commit: Bank Guardian AI"
git branch -M main
git push -u origin main
```

### Documentation

For detailed instructions, see [REPOSITORY_MIGRATION_GUIDE.md](./REPOSITORY_MIGRATION_GUIDE.md)

### Result

After migration:
- ✅ Clean git history (single initial commit)
- ✅ All files preserved
- ✅ Ready for deployment at new location
- ✅ No commit history from original repo

