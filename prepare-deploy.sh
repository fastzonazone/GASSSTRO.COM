#!/bin/bash

# GASsstro - Quick Deployment Script
# This script helps prepare your repository for deployment

set -e  # Exit on error

echo "🚀 GASsstro Deployment Preparation"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "server.py" ]; then
    echo "❌ Error: server.py not found. Are you in the timbrobro directory?"
    exit 1
fi

echo "✅ Found server.py - we're in the right directory"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found"
    echo "📝 Creating .env from template..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
        echo "⚠️  IMPORTANT: Edit .env and fill in your credentials!"
    else
        echo "❌ Error: .env.example not found"
        exit 1
    fi
else
    echo "✅ .env file exists"
fi

echo ""
echo "🔍 Checking Git status..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

# Check if .gitignore exists and is correct
if [ -f ".gitignore" ]; then
    if grep -q ".env" ".gitignore"; then
        echo "✅ .gitignore properly configured"
    else
        echo "⚠️  .env not in .gitignore - this is dangerous!"
        echo "   Adding .env to .gitignore..."
        echo ".env" >> .gitignore
        echo "✅ Updated .gitignore"
    fi
else
    echo "❌ No .gitignore found - creating one..."
    cat > .gitignore << 'EOF'
# Environment variables
.env
.env.local
.env.production
*.env

# Database
orders.db
*.db

# Python
__pycache__/
*.pyc

# Exports
exports/
*.stl

# System
.DS_Store
EOF
    echo "✅ Created .gitignore"
fi

echo ""
echo "📋 Pre-Deployment Checklist:"
echo ""
echo "Before deploying, make sure you have:"
echo ""
echo "  1. ✅ Stripe account with LIVE API keys"
echo "  2. ✅ SMTP credentials for orders@gassstro.com"
echo "  3. ✅ GitHub account"
echo "  4. ✅ Render.com account"
echo ""
echo "Next steps:"
echo ""
echo "  1. 📝 Edit .env with your test credentials for local development"
echo "  2. 🧪 Test locally: python3 server.py"
echo "  3. 📤 Push to GitHub: git add . && git commit -m 'Ready for deployment' && git push"
echo "  4. 🚀 Follow RENDER_SETUP.md to deploy backend"
echo "  5. 🌐 Enable GitHub Pages for frontend"
echo "  6. ✅ Complete LAUNCH_CHECKLIST.md"
echo ""
echo "📚 Documentation:"
echo "  - RENDER_SETUP.md - Detailed Render.com deployment guide"
echo "  - LAUNCH_CHECKLIST.md - Pre-launch verification checklist"
echo "  - README.md - Project overview and local development"
echo ""
echo "🎉 Preparation complete!"
echo ""
echo "⚠️  REMINDER: Never commit .env files to Git!"
echo "   Your secrets are protected by .gitignore"
echo ""
