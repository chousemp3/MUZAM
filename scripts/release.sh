#!/bin/bash

# 🎵 MUZAM GitHub Release Script
# Automates the process of creating a new release

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎵 MUZAM Release Script${NC}"
echo -e "${BLUE}========================${NC}"

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Check if we're on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo -e "${YELLOW}⚠️  Warning: You're not on the main branch (current: $current_branch)${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ Error: You have uncommitted changes${NC}"
    git status --short
    exit 1
fi

# Get version from user
echo -e "\n${BLUE}📋 Release Information${NC}"
read -p "Enter version (e.g., v1.0.0): " version
read -p "Enter release title: " title
read -p "Enter release description: " description

# Validate version format
if [[ ! $version =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}❌ Error: Version must be in format v1.0.0${NC}"
    exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^$version$"; then
    echo -e "${RED}❌ Error: Tag $version already exists${NC}"
    exit 1
fi

# Run tests
echo -e "\n${BLUE}🧪 Running tests...${NC}"
if ! python test_muzam.py; then
    echo -e "${RED}❌ Tests failed! Please fix before releasing.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Tests passed!${NC}"

# Create git tag
echo -e "\n${BLUE}🏷️  Creating git tag...${NC}"
git tag -a "$version" -m "$title"

# Push tag
echo -e "${BLUE}⬆️  Pushing tag to GitHub...${NC}"
git push origin "$version"

# Create GitHub release (requires gh CLI)
if command -v gh &> /dev/null; then
    echo -e "\n${BLUE}🚀 Creating GitHub release...${NC}"
    gh release create "$version" \
        --title "$title" \
        --notes "$description" \
        --latest
    
    echo -e "${GREEN}✅ Release created successfully!${NC}"
    echo -e "${BLUE}🔗 View at: https://github.com/$(gh repo view --json owner,name -q '.owner.login + "/" + .name')/releases/tag/$version${NC}"
else
    echo -e "\n${YELLOW}⚠️  GitHub CLI not found. Please create the release manually at:${NC}"
    echo -e "${BLUE}https://github.com/YOUR_USERNAME/MUZAM/releases/new?tag=$version${NC}"
fi

echo -e "\n${GREEN}🎉 Release process completed!${NC}"
echo -e "${BLUE}Don't forget to:${NC}"
echo -e "• Update the Docker image if needed"
echo -e "• Announce the release on social media"
echo -e "• Update documentation if needed"
