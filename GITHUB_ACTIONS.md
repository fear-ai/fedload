# GitHub Actions CI/CD Guide

This guide explains how to enable, configure, and use the GitHub Actions CI/CD pipeline for the FedLoad project.

## Overview

The CI/CD pipeline provides:
- **Automated Testing**: Run tests on Python 3.11 and 3.12
- **Code Quality**: Linting, security scanning, and type checking
- **Docker Build**: Multi-platform container images
- **Security Scanning**: Vulnerability detection with Trivy
- **Optional Deployment**: Configurable production deployment

## Quick Start

### 1. Enable GitHub Actions

The workflow is **automatically enabled** when you push to the `main` or `develop` branches. No additional setup required for basic CI/CD.

### 2. View Pipeline Status

- Go to your repository on GitHub
- Click the **"Actions"** tab
- View running and completed workflows

### 3. Check Build Status

The pipeline runs on:
- **Push** to `main` or `develop` branches
- **Pull requests** to `main` branch
- **Release** creation

## Configuration

### Environment Variables

Set these in your repository settings under **Settings > Secrets and variables > Actions**:

#### Required for Container Registry
```bash
# Automatically available - no setup needed
GITHUB_TOKEN  # Provided by GitHub
```

#### Optional for Deployment
```bash
# Add these as repository variables if using deployment
ENABLE_DEPLOYMENT=true  # Set to enable deployment
```

### Repository Settings

1. **Enable Actions**: Settings > Actions > General > "Allow all actions"
2. **Container Registry**: Settings > Actions > General > "Read and write permissions"
3. **Environments**: Settings > Environments > Create "production" environment

## Pipeline Stages

### 1. Test Stage

```yaml
# Runs on: Python 3.11, 3.12
- Code checkout
- Dependency installation
- Linting (flake8)
- Security checks (bandit, safety)
- Unit tests with coverage
- Upload coverage to Codecov
```

**Artifacts Generated**:
- Test coverage reports
- Security scan results
- Linting reports

### 2. Build Stage

```yaml
# Runs on: Push to main/develop (not PRs)
- Docker multi-platform build (amd64, arm64)
- Push to GitHub Container Registry
- Generate build metadata
- Cache optimization
```

**Container Registry**: `ghcr.io/yourusername/fedloadw`

### 3. Security Stage

```yaml
# Runs on: After successful build
- Trivy vulnerability scanning
- Upload results to GitHub Security tab
- SARIF format reports
```

### 4. Deploy Stage (Optional)

```yaml
# Runs on: Push to main + ENABLE_DEPLOYMENT=true
- Production environment deployment
- Configurable deployment commands
- Rollback capabilities
```

## Enabling/Disabling Features

### Disable Deployment (Default)

Deployment is **disabled by default**. The pipeline will build and test but not deploy.

### Enable Deployment

1. **Repository Variables**:
   ```bash
   # Settings > Secrets and variables > Actions > Variables
   ENABLE_DEPLOYMENT = true
   ```

2. **Environment Protection**:
   ```bash
   # Settings > Environments > production
   - Add required reviewers
   - Add deployment branches (main)
   - Add environment secrets if needed
   ```

### Disable Specific Stages

Edit `.github/workflows/ci-cd.yml`:

```yaml
# Disable security scanning
security:
  if: false  # Add this line

# Disable multi-platform builds
build:
  steps:
    - name: Build and push Docker image
      with:
        platforms: linux/amd64  # Remove linux/arm64
```

### Enable Additional Features

#### 1. Slack Notifications

```yaml
# Add to notify job
- name: Slack Notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

#### 2. Deploy to Multiple Environments

```yaml
# Add staging deployment
deploy-staging:
  needs: [test, build]
  if: github.ref == 'refs/heads/develop'
  environment: staging
  # ... deployment steps
```

## Container Registry

### Image Tags

The pipeline creates multiple tags:

```bash
# Branch-based tags
ghcr.io/yourusername/fedloadw:main
ghcr.io/yourusername/fedloadw:develop

# Commit-based tags
ghcr.io/yourusername/fedloadw:main-abc1234

# Release tags (on GitHub releases)
ghcr.io/yourusername/fedloadw:v1.0.0
ghcr.io/yourusername/fedloadw:1.0
```

### Using Images

```bash
# Pull latest main branch image
docker pull ghcr.io/yourusername/fedloadw:main

# Use in docker-compose.yml
services:
  fedload-api:
    image: ghcr.io/yourusername/fedloadw:main
```

## Security Features

### 1. Vulnerability Scanning

- **Trivy**: Scans container images for vulnerabilities
- **Results**: Available in GitHub Security tab
- **Format**: SARIF for integration with GitHub

### 2. Code Security

- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability checker
- **Results**: Uploaded as artifacts

### 3. Supply Chain Security

- **Dependency pinning**: Exact versions in requirements.txt
- **Multi-stage builds**: Minimal attack surface
- **Non-root containers**: Security best practices

## Monitoring and Debugging

### View Logs

1. **GitHub UI**: Actions tab > Select workflow > View logs
2. **Download artifacts**: Test results, security reports

### Debug Failed Builds

```yaml
# Add debug step to workflow
- name: Debug
  if: failure()
  run: |
    echo "Debug information"
    env
    ls -la
    docker images
```

### Re-run Failed Jobs

1. Go to failed workflow
2. Click "Re-run failed jobs"
3. Or "Re-run all jobs" for complete retry

## Performance Optimization

### 1. Caching

The pipeline uses multiple caching strategies:

```yaml
# Pip cache
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# Docker layer cache
cache-from: type=gha
cache-to: type=gha,mode=max
```

### 2. Parallel Execution

- Tests run in parallel across Python versions
- Build and security stages run independently
- Matrix builds for multiple configurations

### 3. Conditional Execution

- PRs skip build and deployment
- Security scans only on successful builds
- Deployment only on main branch

## Troubleshooting

### Common Issues

#### 1. Permission Denied

```bash
# Error: Permission denied to write to registry
# Solution: Check repository settings
Settings > Actions > General > Workflow permissions > Read and write
```

#### 2. Test Failures

```bash
# Error: Tests fail in CI but pass locally
# Solution: Check environment differences
- Python version differences
- Missing environment variables
- Dependency version conflicts
```

#### 3. Docker Build Failures

```bash
# Error: Docker build fails
# Solution: Check Dockerfile and dependencies
- Verify base image availability
- Check dependency installation
- Review build context size
```

#### 4. Deployment Not Running

```bash
# Error: Deployment stage skipped
# Solution: Check conditions
- ENABLE_DEPLOYMENT variable set to 'true'
- Push to main branch (not PR)
- Environment configured correctly
```

### Debug Commands

```bash
# Local testing of workflow
act -j test  # Requires 'act' tool

# Test Docker build locally
docker build -t fedload:test .

# Validate workflow syntax
# Use GitHub's workflow validator or VS Code extension
```

## Best Practices

### 1. Branch Protection

```bash
# Settings > Branches > Add rule for 'main'
- Require status checks to pass
- Require branches to be up to date
- Include administrators
- Restrict pushes to matching branches
```

### 2. Security

```bash
# Use secrets for sensitive data
- Never commit API keys or passwords
- Use environment-specific secrets
- Rotate secrets regularly
```

### 3. Testing

```bash
# Comprehensive test coverage
- Unit tests for all functions
- Integration tests for APIs
- Security tests for vulnerabilities
```

### 4. Documentation

```bash
# Keep documentation updated
- Update README for new features
- Document configuration changes
- Maintain changelog
```

## Advanced Configuration

### Custom Deployment

Edit the deploy job in `.github/workflows/ci-cd.yml`:

```yaml
deploy:
  steps:
  - name: Deploy to production
    run: |
      # Your custom deployment commands
      kubectl set image deployment/fedload fedload=${{ needs.build.outputs.image-tag }}
      kubectl rollout status deployment/fedload
```

### Multi-Environment Pipeline

```yaml
# Add environment-specific jobs
deploy-staging:
  if: github.ref == 'refs/heads/develop'
  environment: staging

deploy-production:
  if: github.ref == 'refs/heads/main'
  environment: production
  needs: deploy-staging
```

### Integration with External Services

```yaml
# Add external service notifications
- name: Notify monitoring
  run: |
    curl -X POST ${{ secrets.MONITORING_WEBHOOK }} \
      -d '{"status": "deployed", "version": "${{ github.sha }}"}'
```

## Cost Optimization

### 1. Efficient Workflows

- Use conditional execution
- Cache dependencies aggressively
- Minimize build matrix size

### 2. Resource Management

- Use appropriate runner sizes
- Optimize Docker builds
- Clean up artifacts regularly

### 3. Monitoring Usage

- Check Actions usage in Settings > Billing
- Monitor workflow execution times
- Optimize slow steps 