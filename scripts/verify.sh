#!/bin/bash

# ReSan Bank - Project Verification

# Get the project root directory
cd "$(dirname "$0")/.." || exit

echo "🔍 ReSan Bank - Project Verification"
echo "===================================="
echo ""

# Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    echo "   ✅ Python found: $(python3 --version)"
else
    echo "   ❌ Python not found"
    exit 1
fi

# Check main.py syntax
echo ""
echo "2. Checking main.py syntax..."
if python3 -m py_compile main.py 2>/dev/null; then
    echo "   ✅ main.py syntax valid"
else
    echo "   ❌ main.py has syntax errors"
    exit 1
fi

# Check data file
echo ""
echo "3. Checking resan_data.json..."
if [ -f "resan_data.json" ]; then
    if python3 -c "import json; json.load(open('resan_data.json'))" 2>/dev/null; then
        echo "   ✅ resan_data.json valid JSON"
    else
        echo "   ❌ resan_data.json invalid JSON"
        exit 1
    fi
else
    echo "   ⚠️  resan_data.json not found (will be created on first run)"
fi

# Check .env file
echo ""
echo "4. Checking .env configuration..."
if [ -f "config/.env" ] || [ -f ".env" ]; then
    echo "   ✅ .env file found (SMS may be enabled)"
else
    echo "   ℹ️  No .env file (running in dev mode)"
fi

# Check .env.example
echo ""
echo "5. Checking config/.env.example..."
if [ -f "config/.env.example" ]; then
    if grep -q "your_account_sid_here" config/.env.example; then
        echo "   ✅ config/.env.example has placeholders (no real credentials)"
    else
        echo "   ⚠️  config/.env.example may contain real credentials"
    fi
else
    echo "   ❌ config/.env.example not found"
fi

# Check frontend files
echo ""
echo "6. Checking frontend files..."
if [ -f "frontend/index.html" ] && [ -f "frontend/style.css" ] && [ -f "frontend/app.js" ]; then
    echo "   ✅ All frontend files present"
else
    echo "   ❌ Missing frontend files"
    exit 1
fi

# Check theme buttons in HTML
echo ""
echo "7. Checking theme system..."
if grep -q "theme-toggle" frontend/index.html && grep -q "theme-toggle" frontend/style.css; then
    echo "   ✅ Theme system implemented"
else
    echo "   ❌ Theme system not found"
    exit 1
fi

# Check documentation
echo ""
echo "8. Checking documentation..."
if [ -f "docs/DOCUMENTATION.md" ] && [ -f "README.md" ]; then
    echo "   ✅ Documentation files present"
else
    echo "   ❌ Missing documentation"
    exit 1
fi

# Check start scripts
echo ""
echo "9. Checking start scripts..."
if [ -f "scripts/start.sh" ] && [ -f "scripts/start.bat" ]; then
    echo "   ✅ Start scripts present"
else
    echo "   ❌ Missing start scripts"
    exit 1
fi

# Check deployment files
echo ""
echo "10. Checking deployment files..."
if [ -f "config/Procfile" ] && [ -f "config/runtime.txt" ] && [ -f "requirements.txt" ]; then
    echo "   ✅ Deployment files present"
else
    echo "   ❌ Missing deployment files"
    exit 1
fi

echo ""
echo "===================================="
echo "✅ All checks passed!"
echo ""
echo "Your project is ready to run:"
echo "  ./scripts/start.sh"
echo ""
echo "Or deploy to production!"
echo "===================================="
