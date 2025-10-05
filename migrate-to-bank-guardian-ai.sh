#!/bin/bash

################################################################################
# Repository Migration Script
# 
# This script migrates the anthos-guardian-agent repository to bank-guardian-ai
# with a clean commit history (no previous commits).
#
# Usage: ./migrate-to-bank-guardian-ai.sh
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SOURCE_REPO="https://github.com/futureaiitofficial/anthos-guardian-agent.git"
TARGET_REPO="https://github.com/lahari17/bank-guardian-ai.git"
TEMP_DIR="bank-guardian-ai-migration-temp"
COMMIT_MESSAGE="Initial commit: Bank Guardian AI - AI-powered fraud detection system for Bank of Anthos"

################################################################################
# Functions
################################################################################

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "$1"
}

################################################################################
# Main Script
################################################################################

print_header "Bank Guardian AI - Repository Migration Script"

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git and try again."
    exit 1
fi
print_success "Git is installed"

# Check if temporary directory already exists
if [ -d "$TEMP_DIR" ]; then
    print_warning "Temporary directory '$TEMP_DIR' already exists."
    read -p "Do you want to remove it and continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$TEMP_DIR"
        print_success "Removed existing temporary directory"
    else
        print_error "Migration cancelled"
        exit 1
    fi
fi

# Step 1: Clone the source repository
print_header "Step 1: Cloning source repository"
print_info "Cloning from: $SOURCE_REPO"
git clone "$SOURCE_REPO" "$TEMP_DIR"
cd "$TEMP_DIR"
print_success "Source repository cloned successfully"

# Step 2: Remove git history
print_header "Step 2: Removing git history"
rm -rf .git
print_success "Git history removed"

# Step 3: Initialize new git repository
print_header "Step 3: Initializing new git repository"
git init
print_success "New git repository initialized"

# Step 4: Configure git (optional - use global config if available)
print_header "Step 4: Checking git configuration"
GIT_USER_NAME=$(git config user.name || echo "")
GIT_USER_EMAIL=$(git config user.email || echo "")

if [ -z "$GIT_USER_NAME" ] || [ -z "$GIT_USER_EMAIL" ]; then
    print_warning "Git user configuration not found"
    read -p "Enter your name: " user_name
    read -p "Enter your email: " user_email
    git config user.name "$user_name"
    git config user.email "$user_email"
    print_success "Git user configured"
else
    print_success "Using existing git configuration: $GIT_USER_NAME <$GIT_USER_EMAIL>"
fi

# Step 5: Add remote repository
print_header "Step 5: Adding remote repository"
print_info "Target repository: $TARGET_REPO"
git remote add origin "$TARGET_REPO"
print_success "Remote repository added"

# Step 6: Stage all files
print_header "Step 6: Staging all files"
git add .
FILE_COUNT=$(git diff --cached --numstat | wc -l)
print_success "Staged $FILE_COUNT files"

# Step 7: Create initial commit
print_header "Step 7: Creating initial commit"
git commit -m "$COMMIT_MESSAGE"
print_success "Initial commit created"

# Step 8: Show summary
print_header "Migration Summary"
print_info "Repository: $(pwd)"
print_info "Remote URL: $(git remote get-url origin)"
print_info "Branch: $(git branch --show-current)"
print_info "Commit count: $(git rev-list --count HEAD)"
print_info "Latest commit: $(git log -1 --oneline)"

# Step 9: Confirm push
print_header "Step 9: Ready to push"
print_warning "This will push to: $TARGET_REPO"
print_warning "This operation will overwrite the remote repository if it already has content!"
read -p "Do you want to proceed with pushing? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Pushing to remote repository..."
    git branch -M main
    
    # Try to push, handle existing remote content
    if git push -u origin main 2>&1 | grep -q "rejected"; then
        print_warning "Remote has existing content. Forcing push to create clean history..."
        print_warning "This will overwrite any existing content in the remote repository!"
        read -p "Are you absolutely sure? (type 'yes' to confirm) " confirmation
        if [ "$confirmation" = "yes" ]; then
            git push -u origin main --force
            print_success "Repository pushed successfully (forced)"
        else
            print_error "Push cancelled"
            exit 1
        fi
    else
        print_success "Repository pushed successfully"
    fi
else
    print_warning "Push cancelled. You can manually push later using:"
    print_info "  cd $TEMP_DIR"
    print_info "  git push -u origin main"
    exit 0
fi

# Step 10: Cleanup instructions
print_header "Migration Complete!"
print_success "Repository successfully migrated to: $TARGET_REPO"
print_info ""
print_info "Next steps:"
print_info "1. Visit: https://github.com/lahari17/bank-guardian-ai"
print_info "2. Verify all files are present"
print_info "3. Check that only one commit exists"
print_info "4. Update repository settings (branch protection, secrets, etc.)"
print_info ""
print_info "The migrated repository is located at: $(pwd)"
print_info "You can safely delete this directory after verification:"
print_info "  cd .. && rm -rf $TEMP_DIR"

print_header "Thank you for using Bank Guardian AI!"
