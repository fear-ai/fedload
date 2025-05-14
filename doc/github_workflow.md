# GitHub Workflow Documentation

## Branch Structure

### Main Branches
- `main` - Production branch
  - Always stable and deployable
  - Protected branch with required reviews
  - Only updated through releases or hotfixes
  - Requires passing CI checks
  - No direct pushes allowed

- `develop` - Development branch
  - Integration branch for features
  - Contains latest delivered development changes
  - Protected branch with required reviews

### Supporting Branches
- `feature/*` - Feature branches
  - Branch from: `develop`
  - Merge back to: `develop`
  - Naming convention: `feature/feature-name`
  - Example: `feature/pdf-extraction`

- `release/*` - Release preparation branches
  - Branch from: `develop`
  - Merge back to: `develop` and `main`
  - Naming convention: `release/vX.Y.Z`
  - Example: `release/v1.0.0`

- `hotfix/*` - Emergency fixes
  - Branch from: `main`
  - Merge back to: `main` and `develop`
  - Naming convention: `hotfix/description`
  - Example: `hotfix/security-patch`

## Workflow Processes

### Feature Development
1. Create feature branch from develop:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. Develop and commit changes:
   ```bash
   git add .
   git commit -m "feat: description of changes"
   ```

3. Push to remote:
   ```bash
   git push -u origin feature/your-feature-name
   ```

4. Create pull request to develop
5. Wait for CI checks and reviews
6. Merge after approval

### Release Process
1. Create release branch:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/vX.Y.Z
   ```

2. Update version numbers and documentation
3. Create pull request to main
4. Wait for CI checks and reviews
5. Merge to main after approval
6. Create version tag:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

7. Merge back to develop:
   ```bash
   git checkout develop
   git merge release/vX.Y.Z
   git push origin develop
   ```

### Hotfix Process
1. Create hotfix branch:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/description
   ```

2. Fix the issue and commit:
   ```bash
   git add .
   git commit -m "fix: description of fix"
   ```

3. Create pull requests to both main and develop
4. Wait for CI checks and reviews
5. Merge after approval

## CI/CD Pipeline

### Continuous Integration
- Runs on: push to main/develop and pull requests
- Python versions: 3.8, 3.9, 3.10
- Checks:
  - Linting (flake8)
  - Testing (pytest)
  - Security (bandit, safety)
  - Code quality (CodeQL)

### Continuous Deployment
- Automatic release creation on version tags
- Release notes generation
- Documentation updates

## Branch Protection Rules

### Main Branch
- Require pull request reviews
  - Minimum 1 approval
  - Dismiss stale approvals
  - Require review from code owners
- Require status checks
  - test (3.8)
  - test (3.9)
  - test (3.10)
  - security
  - CodeQL
- Require branches to be up to date
- No direct pushes
- No force pushes
- No branch deletion

### Develop Branch
- Require pull request reviews
  - Minimum 1 approval
  - Dismiss stale approvals
- Require status checks
  - test (3.8)
  - test (3.9)
  - test (3.10)
  - security
  - CodeQL
- Require branches to be up to date
- No direct pushes
- No force pushes
- No branch deletion

## Issue and Pull Request Templates

### Issue Templates
1. Bug Report
   - Environment details
   - Reproduction steps
   - Expected vs actual behavior
   - Logs and screenshots

2. Feature Request
   - Problem description
   - Proposed solution
   - Impact analysis
   - Technical details

3. Documentation
   - Documentation type
   - Current vs suggested changes
   - Priority level
   - Context

### Pull Request Template
- Description
- Type of change
- Related issues
- Testing details
- Documentation updates
- Checklist
- Deployment notes

## Versioning

### Semantic Versioning
- MAJOR.MINOR.PATCH
- MAJOR: Incompatible API changes
- MINOR: Backwards-compatible functionality
- PATCH: Backwards-compatible bug fixes

### Version Tags
- Format: vX.Y.Z
- Example: v1.0.0
- Created automatically on release
- Includes release notes

## Dependencies

### Core Dependencies
- fastapi
- uvicorn
- requests
- beautifulsoup4
- schedule
- spacy
- newspaper3k
- trafilatura
- html2text
- pdfminer.six

### Development Dependencies
- pytest
- pytest-cov
- flake8
- bandit
- safety
- black
- mypy

## Best Practices

### Commits
- Use conventional commit messages
- Keep commits focused and atomic
- Reference issues in commit messages
- Sign commits when possible

### Pull Requests
- Keep PRs small and focused
- Include tests for new features
- Update documentation
- Request reviews from relevant team members

### Code Review
- Check for security issues
- Verify test coverage
- Ensure documentation is updated
- Consider performance implications

### Documentation
- Keep README up to date
- Document API changes
- Update configuration guides
- Maintain changelog

Verify the current Git configuration and status:
```bash
git status
```

Check the remote repository configuration:
```bash
git remote -v
```

**Git Configuration Recommendations**:

   **Branch Setup**:
   ```bash
   # Create development branch
   git checkout -b develop
   ```
   # Create feature branch template
   ```bash
   git checkout -b feature/template
   git push -u origin feature/template
   ```

**GitHub Workflow Setup**:
   - Create `.github/workflows` directory
   - Add CI/CD workflows for:
     - Python testing
     - Code linting
     - Security scanning

**Repository Settings** (in GitHub UI):
   - Set up issue templates
   - Configure pull request templates
   - Enable GitHub Actions


GitHub workflow files for CI/CD, testing, and code quality checks.
```bash
mkdir -p .github/workflows
```

```yaml:.github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10"]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        python -m spacy download en_core_web_sm
        
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
        
    - name: Test with pytest
      run: |
        pip install pytest pytest-cov
        pytest tests/ --cov=./ --cov-report=xml
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Bandit security linter
      run: |
        pip install bandit
        bandit -r . -c pyproject.toml
        
    - name: Run Safety check
      run: |
        pip install safety
        safety check
```

Workflow for automated dependency updates:
```yaml:.github/workflows/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "maintainers"
    assignees:
      - "maintainers"
    labels:
      - "dependencies"
      - "python"
    commit-message:
      prefix: "pip"
      include: "scope"
    ignore:
      - dependency-name: "spacy"
        versions: ["3.0.0", "3.1.0"]
      - dependency-name: "fastapi"
        versions: ["0.68.0", "0.68.1"]
```

Workflow for code quality checks:
```github actions workflow:.github/workflows/codeql.yml
name: "CodeQL"

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 0 * * 0'

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [ 'python' ]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: ${{ matrix.language }}

    - name: Autobuild
      uses: github/codeql-action/autobuild@v2

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
      with:
        category: "/language:${{matrix.language}}"
```

Workflow for release management:
```github actions workflow:.github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          python -m spacy download en_core_web_sm
          
      - name: Run tests
        run: |
          pip install pytest
          pytest tests/
          
      - name: Create Release
        id: create_release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
          
      - name: Generate Release Notes
        run: |
          echo "## Changes" >> $GITHUB_WORKSPACE/release_notes.md
          git log --pretty=format:"- %s" $(git describe --tags --abbrev=0)..HEAD >> $GITHUB_WORKSPACE/release_notes.md
          
      - name: Update Release Notes
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            const releaseNotes = fs.readFileSync('$GITHUB_WORKSPACE/release_notes.md', 'utf8');
            github.rest.repos.updateRelease({
              owner: context.repo.owner,
              repo: context.repo.repo,
              release_id: ${{ steps.create_release.outputs.id }},
              body: releaseNotes
            });
```


GitHub workflow files:

1. **CI Workflow** (`.github/workflows/ci.yml`):
   - Runs on push to main/develop and pull requests
   - Tests with multiple Python versions (3.8, 3.9, 3.10)
   - Includes linting with flake8
   - Runs pytest with coverage
   - Uploads coverage to Codecov
   - Includes security checks with Bandit and Safety

2. **Dependabot Configuration** (`.github/dependabot.yml`):
   - Weekly dependency updates
   - Limited to 10 open PRs
   - Specific reviewers and labels
   - Ignores certain versions of critical dependencies
   - Custom commit message format

3. **CodeQL Analysis** (`.github/workflows/codeql.yml`):
   - Security analysis for Python code
   - Runs on push, PR, and weekly schedule
   - Uses GitHub's CodeQL for static analysis
   - Reports security vulnerabilities

4. **Release Workflow** (`.github/workflows/release.yml`):
   - Triggers on version tags (v*)
   - Runs tests before release
   - Creates GitHub release
   - Generates release notes from git history
   - Updates release with changelog


To complete:
1. Enable GitHub Actions in your repository settings
2. Set up Codecov integration (if desired)
3. Configure branch protection rules
4. Add the following to your requirements.txt:
   ```
   flake8
   pytest
   pytest-cov
   bandit
   safety
   ```

```pip requirements:requirements.txt
# Core dependencies
fastapi
uvicorn
requests
beautifulsoup4
schedule
spacy
newspaper3k
trafilatura
html2text
pdfminer.six

# Testing and CI/CD
pytest
pytest-cov
flake8
bandit
safety
black
mypy
```


Branch protection in GitHub:

1. **Access Branch Protection Settings**:
   - Go to your GitHub repository
   - Click on "Settings"
   - Click on "Branches" in the left sidebar
   - Under "Branch protection rules", click "Add rule"

2. **Main Branch Protection**:
   ```
   Branch name pattern: main
   
   Protect matching branches:
   ✓ Require a pull request before merging
     ✓ Require approvals
       - Required number of approvals: 1
     ✓ Dismiss stale pull request approvals when new commits are pushed
     ✓ Require review from Code Owners
   
   ✓ Require status checks to pass before merging
     ✓ Require branches to be up to date before merging
     Status checks that are required:
     - test (3.8)
     - test (3.9)
     - test (3.10)
     - security
     - CodeQL
   
   ✓ Require conversation resolution before merging
   
   ✓ Include administrators
   
   ✓ Allow force pushes: Disabled
   
   ✓ Allow deletions: Disabled
   ```

3. **Develop Branch Protection**:
   ```
   Branch name pattern: develop
   
   Protect matching branches:
   ✓ Require a pull request before merging
     ✓ Require approvals
       - Required number of approvals: 1
     ✓ Dismiss stale pull request approvals when new commits are pushed
   
   ✓ Require status checks to pass before merging
     ✓ Require branches to be up to date before merging
     Status checks that are required:
     - test (3.8)
     - test (3.9)
     - test (3.10)
     - security
     - CodeQL
   
   ✓ Require conversation resolution before merging
   
   ✓ Include administrators
   
   ✓ Allow force pushes: Disabled
   
   ✓ Allow deletions: Disabled
   ```

4. **Additional Settings**:
   - Under "Settings" > "Actions" > "General":
     - Set "Actions permissions" to "Allow all actions and reusable workflows"
     - Enable "Read and write permissions" for workflows
     - Enable "Fork pull request workflows from outside collaborators"

5. **Required Status Checks**:
   The following checks must pass before merging:
   - `test (3.8)` - Python 3.8 tests
   - `test (3.9)` - Python 3.9 tests
   - `test (3.10)` - Python 3.10 tests
   - `security` - Security checks
   - `CodeQL` - Code quality analysis

6. **Branch Naming Conventions**:
   ```
   Feature branches: feature/*
   Release branches: release/*
   Hotfix branches: hotfix/*
   ```

7. **Pull Request Template**:
   Create `.github/pull_request_template.md`:
   ```markdown
   ## Description
   [Description of changes]

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Manual testing performed
   - [ ] All tests pass

   ## Documentation
   - [ ] README updated
   - [ ] API documentation updated
   - [ ] Code comments added/updated

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] No linter errors
   - [ ] No security issues
   - [ ] Dependencies updated
   ```

8. **Issue Templates**:
   Create `.github/ISSUE_TEMPLATE/` with:
   - `bug_report.md`
   - `feature_request.md`
   - `documentation.md`

