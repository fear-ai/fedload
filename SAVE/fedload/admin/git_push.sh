#!/bin/bash
# 🚀 Push Fed Load project to GitHub

REPO_NAME="fed_load"
GH_USER="your_github_username"  # Replace this

git init
git add fed_load
git commit -m "Initial commit of Fed Load project"
gh repo create $GH_USER/$REPO_NAME --public --source=. --remote=origin --push
echo "✅ Pushed to GitHub: https://github.com/$GH_USER/$REPO_NAME"
