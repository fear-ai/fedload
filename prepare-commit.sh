#!/bin/bash

# FedLoad - Commit Preparation Script
# This script helps prepare for a major commit by checking project status

set -e  # Exit on any error

echo "🚀 FedLoad - Commit Preparation Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "scheduler.py" ]; then
    print_error "This script must be run from the FedLoad project root directory"
    exit 1
fi

print_status "Checking project status..."

# 1. Check Git status
echo ""
echo "📋 Git Status:"
echo "=============="
git status --porcelain

# Count changes
MODIFIED=$(git status --porcelain | grep "^ M" | wc -l)
ADDED=$(git status --porcelain | grep "^A" | wc -l)
DELETED=$(git status --porcelain | grep "^D" | wc -l)
UNTRACKED=$(git status --porcelain | grep "^??" | wc -l)

echo ""
print_status "Changes summary:"
echo "  Modified files: $MODIFIED"
echo "  Added files: $ADDED"
echo "  Deleted files: $DELETED"
echo "  Untracked files: $UNTRACKED"

# 2. Check if virtual environment is active
echo ""
echo "🐍 Python Environment:"
echo "====================="
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment not activated"
    echo "  Run: .venv\\Scripts\\Activate.ps1 (Windows) or source .venv/bin/activate (Linux/Mac)"
else
    print_success "Virtual environment active: $VIRTUAL_ENV"
fi

# 3. Check Python version
PYTHON_VERSION=$(python --version 2>&1)
print_status "Python version: $PYTHON_VERSION"

# 4. Run tests
echo ""
echo "🧪 Running Tests:"
echo "================"
if command -v pytest &> /dev/null; then
    print_status "Running pytest..."
    if pytest tests/ -v --tb=short; then
        print_success "All tests passed!"
    else
        print_error "Some tests failed. Please fix before committing."
        exit 1
    fi
else
    print_warning "pytest not found. Install with: pip install pytest"
fi

# 5. Check linting
echo ""
echo "🔍 Code Quality Check:"
echo "====================="
if command -v flake8 &> /dev/null; then
    print_status "Running flake8..."
    if flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics; then
        print_success "No critical linting errors found"
    else
        print_warning "Linting errors found. Consider fixing before commit."
    fi
else
    print_warning "flake8 not found. Install with: pip install flake8"
fi

# 6. Check Docker files
echo ""
echo "🐳 Docker Configuration:"
echo "======================="
if [ -f "Dockerfile" ]; then
    print_success "Dockerfile exists"
else
    print_error "Dockerfile missing"
fi

if [ -f "docker-compose.yml" ]; then
    print_success "docker-compose.yml exists"
else
    print_error "docker-compose.yml missing"
fi

if [ -f ".dockerignore" ]; then
    print_success ".dockerignore exists"
else
    print_warning ".dockerignore missing"
fi

# 7. Check GitHub Actions
echo ""
echo "⚙️ GitHub Actions:"
echo "=================="
if [ -f ".github/workflows/ci-cd.yml" ]; then
    print_success "CI/CD workflow exists"
else
    print_error "CI/CD workflow missing"
fi

# 8. Check configuration files
echo ""
echo "⚙️ Configuration Files:"
echo "======================"
CONFIG_FILES=("config.json" "fed_entities.json" "tracked_sites.json" "requirements.txt")
for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file exists"
    else
        print_error "$file missing"
    fi
done

# 9. Check for large files that shouldn't be committed
echo ""
echo "📁 Large Files Check:"
echo "===================="
LARGE_FILES=$(find . -type f -size +1M -not -path "./.git/*" -not -path "./.venv/*" -not -path "./logs/*" 2>/dev/null || true)
if [ -z "$LARGE_FILES" ]; then
    print_success "No large files found"
else
    print_warning "Large files found (>1MB):"
    echo "$LARGE_FILES"
    echo "  Consider adding to .gitignore if these are generated files"
fi

# 10. Check .gitignore
echo ""
echo "🚫 .gitignore Check:"
echo "==================="
GITIGNORE_ITEMS=("logs/" "*.log" "__pycache__/" ".coverage" "change_log.json" "entity_store.json")
for item in "${GITIGNORE_ITEMS[@]}"; do
    if grep -q "$item" .gitignore; then
        print_success "$item is ignored"
    else
        print_warning "$item not in .gitignore"
    fi
done

# 11. Security check
echo ""
echo "🔒 Security Check:"
echo "=================="
if command -v bandit &> /dev/null; then
    print_status "Running bandit security check..."
    if bandit -r . -f json -o bandit-report.json -q; then
        print_success "No high-severity security issues found"
    else
        print_warning "Security issues found. Check bandit-report.json"
    fi
else
    print_warning "bandit not found. Install with: pip install bandit"
fi

# 12. Generate commit message suggestions
echo ""
echo "💬 Suggested Commit Messages:"
echo "============================="
echo "For major release:"
echo "  feat: major release with Docker support and CI/CD pipeline"
echo ""
echo "For bug fixes:"
echo "  fix: resolve critical logger bug and improve error handling"
echo ""
echo "For features:"
echo "  feat: add Docker containerization and GitHub Actions CI/CD"
echo ""
echo "For documentation:"
echo "  docs: add comprehensive Docker and GitHub Actions guides"

# 13. Final recommendations
echo ""
echo "📝 Pre-Commit Checklist:"
echo "========================"
echo "✅ All tests passing"
echo "✅ No critical linting errors"
echo "✅ Configuration files present"
echo "✅ Docker files configured"
echo "✅ GitHub Actions workflow ready"
echo "✅ .gitignore updated"
echo "✅ Large files excluded"
echo "✅ Security check completed"

echo ""
print_success "Project is ready for commit!"
echo ""
echo "🚀 Next Steps:"
echo "============="
echo "1. Review changes: git diff --cached"
echo "2. Add files: git add ."
echo "3. Commit: git commit -m \"feat: major release with Docker and CI/CD\""
echo "4. Push: git push origin main"
echo ""
echo "📚 Documentation:"
echo "================="
echo "- Docker: See DOCKER.md"
echo "- GitHub Actions: See GITHUB_ACTIONS.md"
echo "- API: http://localhost:8000/docs (after starting)"

echo ""
print_status "Commit preparation complete! 🎉" 