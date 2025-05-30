# FedLoad Release & Deployment

## 1. Pre-Release Checklist
- All tests pass (unit, integration, system, security)
- Code coverage meets requirements
- Documentation (README, API, config) is up to date
- Changelog is updated
- Version number is bumped (semantic versioning)

## 2. Versioning
- Use semantic versioning: MAJOR.MINOR.PATCH
- Update version in `setup.py` and documentation as needed

## 3. Release Process
- Create a release branch from `develop`:
  ```bash
  git checkout develop
  git pull origin develop
  git checkout -b release/vX.Y.Z
  ```
- Update version, changelog, and documentation
- Push branch and open a pull request to `main`
- Wait for CI checks and code review
- Merge to `main` after approval
- Tag the release:
  ```bash
  git tag -a vX.Y.Z -m "Release vX.Y.Z"
  git push origin vX.Y.Z
  ```
- Merge release branch back to `develop`:
  ```bash
  git checkout develop
  git merge release/vX.Y.Z
  git push origin develop
  ```

## 4. Deployment Steps
- Ensure environment is prepared (Python, virtualenv, dependencies)
- Deploy code to target environment (server, container, etc.)
- Run database migrations or setup scripts if needed
- Start services (API server, scheduler)
- Verify logs and monitoring

## 5. Post-Deployment Verification
- Check API endpoints and UI for correct operation
- Monitor logs for errors or warnings
- Confirm reports and data files are generated as expected
- Notify stakeholders of successful deployment
