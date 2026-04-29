#!/bin/bash

# ReSan Bank - Git Setup Script
# This script helps you set up Git and push to GitHub

# Get the project root directory
cd "$(dirname "$0")/.." || exit

echo "🔧 ReSan Bank - Git Setup"
echo "=========================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first:"
    echo "   macOS: brew install git"
    echo "   Ubuntu: sudo apt install git"
    echo "   Windows: Download from https://git-scm.com/"
    exit 1
fi

echo "✅ Git found: $(git --version)"
echo ""

# Check if already initialized
if [ -d ".git" ]; then
    echo "ℹ️  Git repository already initialized"
    echo ""
else
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
    echo ""
fi

# Check git config
echo "👤 Checking Git configuration..."
GIT_NAME=$(git config user.name)
GIT_EMAIL=$(git config user.email)

if [ -z "$GIT_NAME" ] || [ -z "$GIT_EMAIL" ]; then
    echo ""
    echo "⚠️  Git user not configured. Let's set it up:"
    echo ""
    read -p "Enter your name: " name
    read -p "Enter your email: " email
    
    git config --global user.name "$name"
    git config --global user.email "$email"
    
    echo ""
    echo "✅ Git configured:"
    echo "   Name: $name"
    echo "   Email: $email"
else
    echo "✅ Git configured:"
    echo "   Name: $GIT_NAME"
    echo "   Email: $GIT_EMAIL"
fi

echo ""
echo "=========================="
echo ""

# Check if files are staged
if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "ℹ️  No changes to commit"
else
    echo "📝 Files ready to commit:"
    git status --short
    echo ""
    
    read -p "Do you want to commit these changes? (y/n): " commit_choice
    
    if [ "$commit_choice" = "y" ] || [ "$commit_choice" = "Y" ]; then
        echo ""
        read -p "Enter commit message (or press Enter for default): " commit_msg
        
        if [ -z "$commit_msg" ]; then
            commit_msg="Initial commit: ReSan Bank v2.0.0 with theme system and SMS OTP"
        fi
        
        git add .
        git commit -m "$commit_msg"
        echo ""
        echo "✅ Changes committed!"
    fi
fi

echo ""
echo "=========================="
echo ""

# Check if remote exists
if git remote | grep -q "origin"; then
    echo "ℹ️  Remote 'origin' already configured:"
    git remote -v
    echo ""
else
    echo "🌐 Let's connect to GitHub!"
    echo ""
    echo "First, create a repository on GitHub:"
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: resan-bank"
    echo "3. Choose Public or Private"
    echo "4. DO NOT initialize with README"
    echo "5. Click 'Create repository'"
    echo ""
    read -p "Enter your GitHub repository URL (e.g., https://github.com/username/resan-bank.git): " repo_url
    
    if [ ! -z "$repo_url" ]; then
        git remote add origin "$repo_url"
        echo ""
        echo "✅ Remote added:"
        git remote -v
    fi
fi

echo ""
echo "=========================="
echo ""

# Ask to push
if git remote | grep -q "origin"; then
    read -p "Do you want to push to GitHub now? (y/n): " push_choice
    
    if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
        echo ""
        echo "🚀 Pushing to GitHub..."
        
        # Check if main branch exists, if not rename master to main
        current_branch=$(git branch --show-current)
        if [ "$current_branch" != "main" ]; then
            git branch -M main
        fi
        
        git push -u origin main
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Successfully pushed to GitHub!"
            echo ""
            echo "🎉 Your repository is now live!"
            echo "   View it at: $(git remote get-url origin | sed 's/\.git$//')"
        else
            echo ""
            echo "❌ Push failed. Common issues:"
            echo "   1. Check your GitHub credentials"
            echo "   2. Make sure the repository exists on GitHub"
            echo "   3. Try: git push -u origin main --force (if you're sure)"
        fi
    fi
fi

echo ""
echo "=========================="
echo ""
echo "📚 Next Steps:"
echo ""
echo "1. View your repository on GitHub"
echo "2. Add a description and topics"
echo "3. Enable GitHub Pages (if desired)"
echo "4. Set up branch protection rules"
echo ""
echo "📖 For more Git commands, see: docs/GIT_COMMANDS.md"
echo ""
echo "=========================="
