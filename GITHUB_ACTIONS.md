# GitHub Actions CI/CD Pipeline

This document describes the automated CI/CD pipeline for FedLoad, focusing on GitHub Actions configuration, workflow triggers, and deployment automation.

## 🎯 Pipeline Overview

The FedLoad CI/CD pipeline provides automated testing, security scanning, building, and optional deployment through GitHub Actions workflows.

### Pipeline Stages
1. **Code Quality**: Linting, formatting, type checking
2. **Security**: Dependency scanning, SAST analysis
3. **Testing**: Unit tests, integration tests, coverage reporting
4. **Building**: Docker image creation and registry push
5. **Deployment**: Optional automated deployment to staging/production

## 🔧 Workflow Configuration

### Main Workflow (`.github/workflows/ci-cd.yml`)

**Triggers**:
- Push to `main` and `develop` branches
- Pull requests to `main` branch
- Manual workflow dispatch

**Matrix Strategy**:
- Python versions: 3.11, 3.12, 3.13
- Operating systems: Ubuntu Latest, Windows Latest, macOS Latest

**Key Features**:
- Parallel job execution for faster feedback
- Conditional deployment based on branch and success
- Artifact preservation for debugging
- Comprehensive status reporting

## 📋 Pipeline Jobs

### 1. Code Quality Job
**Purpose**: Ensure code standards and consistency
**Tools**:
- **Black**: Code formatting validation
- **Flake8**: Style guide enforcement
- **MyPy**: Static type checking
- **Bandit**: Security linting

**Failure Conditions**:
- Formatting violations
- Style guide violations
- Type checking errors
- Security vulnerabilities in code

### 2. Security Scanning Job
**Purpose**: Identify security vulnerabilities
**Tools**:
- **Safety**: Python dependency vulnerability scanning
- **Bandit**: Static Application Security Testing (SAST)
- **GitHub Security Advisories**: Automated vulnerability alerts

**Outputs**:
- Security report artifacts
- SARIF files for GitHub Security tab
- Failure on high-severity vulnerabilities

### 3. Testing Job
**Purpose**: Validate functionality and measure coverage
**Test Types**:
- Unit tests for individual components
- Integration tests for component interactions
- Configuration validation tests
- API endpoint tests

**Coverage Requirements**:
- Minimum 80% code coverage
- Coverage reports uploaded to artifacts
- Coverage badge generation

### 4. Build Job
**Purpose**: Create deployable artifacts
**Artifacts**:
- Docker images for API and scheduler services
- Python wheel packages
- Documentation builds

**Registry Integration**:
- GitHub Container Registry (ghcr.io)
- Automated tagging with version and commit SHA
- Multi-architecture builds (AMD64, ARM64)

### 5. Deployment Job (Optional)
**Purpose**: Automated deployment to environments
**Conditions**:
- Only on `main` branch
- All previous jobs successful
- Manual approval for production

**Environments**:
- **Staging**: Automatic deployment from `develop`
- **Production**: Manual approval required

## 🔐 Security Configuration

### Secrets Management
Required repository secrets:
- `DOCKER_REGISTRY_TOKEN`: Container registry authentication
- `DEPLOY_SSH_KEY`: Deployment server access (if using SSH)
- `SLACK_WEBHOOK_URL`: Notification integration (optional)

### Permissions
Workflow permissions configured for:
- `contents: read` - Repository content access
- `packages: write` - Container registry push
- `security-events: write` - Security scanning results

### Security Best Practices
- No secrets in workflow files
- Minimal required permissions
- Dependency pinning with hash verification
- Signed commits verification (optional)

## 📊 Monitoring and Notifications

### Status Reporting
- **GitHub Status Checks**: Required for PR merging
- **Commit Status**: Success/failure indicators on commits
- **PR Comments**: Automated test results and coverage reports

### Notification Channels
- **GitHub Notifications**: Built-in issue and PR notifications
- **Slack Integration**: Optional webhook for team notifications
- **Email Alerts**: GitHub's built-in email notifications

### Metrics and Analytics
- **Workflow Run History**: Success rates and duration trends
- **Test Results**: Historical test performance
- **Security Scan Results**: Vulnerability trend analysis

## 🚀 Deployment Strategies

### Staging Deployment
- **Trigger**: Push to `develop` branch
- **Environment**: Staging server or container platform
- **Validation**: Automated smoke tests post-deployment
- **Rollback**: Automatic on validation failure

### Production Deployment
- **Trigger**: Manual approval after successful staging
- **Strategy**: Blue-green or rolling deployment
- **Validation**: Comprehensive health checks
- **Rollback**: Manual trigger with automated execution

## 🛠️ Workflow Customization

### Environment Variables
Configure pipeline behavior through repository variables:
```yaml
PYTHON_VERSION: "3.12"          # Default Python version
DOCKER_REGISTRY: "ghcr.io"      # Container registry
ENABLE_DEPLOYMENT: "true"       # Enable deployment jobs
COVERAGE_THRESHOLD: "80"        # Minimum coverage percentage
```

### Branch Protection Rules
Recommended settings for `main` branch:
- Require status checks to pass
- Require branches to be up to date
- Require review from code owners
- Restrict pushes to specific users/teams

### Workflow Dispatch Parameters
Manual workflow triggers support:
- **Environment**: Choose deployment target
- **Skip Tests**: For emergency deployments (not recommended)
- **Docker Tag**: Custom tag for container images

## 🔧 Troubleshooting

### Common Issues

**Test Failures**:
- Check test logs in workflow artifacts
- Verify environment setup matches local development
- Review recent changes for breaking modifications

**Security Scan Failures**:
- Review security report artifacts
- Update vulnerable dependencies
- Add security exceptions for false positives (with justification)

**Build Failures**:
- Check Docker build logs
- Verify all dependencies are available
- Review resource limits and timeouts

**Deployment Failures**:
- Check deployment logs and health checks
- Verify infrastructure availability
- Review configuration and secrets

### Debug Mode
Enable debug logging by setting repository variable:
```yaml
ACTIONS_STEP_DEBUG: "true"
```

## 📈 Performance Optimization

### Caching Strategy
- **Python Dependencies**: Cache pip packages between runs
- **Docker Layers**: Leverage layer caching for faster builds
- **Test Data**: Cache test fixtures and data files

### Parallel Execution
- **Matrix Builds**: Run tests across multiple Python versions simultaneously
- **Job Dependencies**: Optimize job dependency graph for maximum parallelism
- **Resource Allocation**: Configure appropriate runner sizes

### Workflow Efficiency
- **Conditional Jobs**: Skip unnecessary jobs based on file changes
- **Early Termination**: Fail fast on critical errors
- **Artifact Management**: Clean up old artifacts automatically

---

**For development setup and local testing, see DEVELOP.md**  
**For project overview and basic usage, see README.md**  
**For Docker deployment instructions, see DOCKER.md** 