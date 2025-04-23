# GitHub Workflow Documentation

## Branch Structure

### Main Branches
- `main` - Production branch
  - Always stable and deployable
  - Protected branch with required reviews
  - Only updated through releases or hotfixes

- `develop` - Development branch
  - Integration branch for features
  - Contains latest delivered development changes
  - Protected branch with required reviews

### Supporting Branches
- `feature/*` - Feature branches
  - Branch from: `develop`
  - Merge back to: `develop`
  - Naming convention: `feature/feature-name`

- `release/*` - Release preparation branches
  - Branch from: `develop`
  - Merge back to: `develop` and `main`
  - Naming convention: `release/vX.Y.Z`

- `hotfix/*` - Emergency fixes
  - Branch from: `main`
  - Merge back to: `main` and `develop`
  - Naming convention: `hotfix/description`

## Versioning Strategy

### Semantic Versioning (MAJOR.MINOR.PATCH)
- MAJOR: Incompatible API changes
- MINOR: Backwards-compatible functionality
- PATCH: Backwards-compatible bug fixes

Example versions:
- v1.0.0 - First stable release
- v1.1.0 - New features, backwards compatible
- v1.1.1 - Bug fixes
- v2.0.0 - Major changes, potentially breaking

## Release Process

### Creating a Release
1. Create release branch:
   ```bash
   git checkout -b release/vX.Y.Z develop
   ```

2. Update version numbers and documentation

3. Test thoroughly

4. Create release tag:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

5. Merge to main:
   ```bash
   git checkout main
   git merge release/vX.Y.Z
   git push origin main
   ```

6. Merge back to develop:
   ```bash
   git checkout develop
   git merge release/vX.Y.Z
   git push origin develop
   ```

7. Delete release branch:
   ```bash
   git branch -d release/vX.Y.Z
   git push origin --delete release/vX.Y.Z
   ```

### GitHub Release Creation
1. Go to GitHub repository
2. Click "Releases"
3. Click "Create a new release"
4. Select the tag (vX.Y.Z)
5. Add release title and description
6. Attach relevant files
7. Click "Publish release"

## Branch Protection Rules

### Main Branch
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- No direct pushes allowed

### Develop Branch
- Require pull request reviews
- Require status checks to pass
- No direct pushes allowed

## Workflow Diagram

```
Feature Development:
develop -> feature/* -> develop

Release Process:
develop -> release/* -> main
develop -> release/* -> develop

Hotfix Process:
main -> hotfix/* -> main
main -> hotfix/* -> develop
```

## Best Practices

1. **Branch Naming**
   - Use lowercase
   - Separate words with hyphens
   - Be descriptive but concise

2. **Commit Messages**
   - Use present tense
   - Be specific and clear
   - Reference issue numbers when applicable

3. **Pull Requests**
   - Include clear description
   - Link related issues
   - Request reviews from relevant team members

4. **Tags**
   - Use semantic versioning
   - Include release notes
   - Sign tags when possible

5. **Merging**
   - Always use pull requests
   - Keep commits clean and focused
   - Resolve conflicts before merging 