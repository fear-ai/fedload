# Project Rules

- Skip congratulatory, summary, or non-technical commentary in all assistant responses. Only provide technical, actionable, or directly relevant content.

# FedLoad Project Rules & Best Practices

## 1. Code Quality
- Follow PEP 8 and use type hints throughout the codebase.
- Document all public functions and classes with clear docstrings.
- Keep functions focused and small; avoid large, monolithic functions.
- Use Black for code formatting, flake8 for linting, and mypy for type checking.

## 2. Branching & Workflow
- Use `main` for production-ready code and `develop` for integration.
- Create feature branches from `develop` using the format `feature/feature-name`.
- Create release branches from `develop` using the format `release/vX.Y.Z`.
- Create hotfix branches from `main` using the format `hotfix/description`.
- Require pull request reviews and passing CI checks before merging.

## 3. Testing
- Write unit, integration, and system tests for all new features and bug fixes.
- Use mocks for external dependencies in unit tests.
- Mark tests appropriately (`unit`, `integration`, `system`, `security`, `slow`).
- Maintain high test coverage and use coverage reports to identify gaps.

## 4. Security
- Validate and sanitize all user and external inputs.
- Use parameterized queries and secure password handling where applicable.
- Run Bandit and Safety as part of the CI pipeline.
- Enforce API key authentication and rate limiting for all API endpoints.

## 5. Documentation
- Keep the README and in-code documentation up to date with all changes.
- Document all API endpoints, configuration options, and usage examples.
- Maintain a changelog for all releases and significant changes.

## 6. Configuration & Data
- Store sensitive data in `.env` files (excluded from version control).
- Use JSON files for configuration and persistent data storage.
- Apply data retention policies for logs and reports as defined in configuration.

## 7. Deployment
- Use Docker for containerization and deployment in production environments.
- Run all tests and update documentation before deploying new versions.
- Monitor logs and system health after deployment and address issues promptly. 