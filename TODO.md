# Open Questions

- [ ] Should we consolidate the documentation files in the `doc` directory?
  - FEDL.txt, FEDR.txt, and FEDR1.txt contain overlapping information
  - Should we create a single comprehensive documentation file?
- [ ] How should we handle the large JSON data files?
  - entity_store.json (359K chars)
  - change_log.json (292K chars)
  - Are these files being properly rotated or cleaned up?
- [ ] Should we split scheduler.py into smaller modules?
  - Currently 753 lines long
  - Might benefit from better organization

# Known Bugs/Limitations

- [ ] Test Logging Issues:
  - test_logging.py fails due to FastAPI app.state.nlp not being initialized
  - Need to mock or properly initialize the FastAPI app state for tests
- [ ] File Management:
  - Temporary directories are being created but might not always be cleaned up properly
  - Need to verify all temp files are being properly deleted after use
- [ ] Configuration:
  - Some configuration values might not be properly validated
  - Need to add more robust validation for config parameters

# Future Plans

## Architecture & Modularity
- [ ] **PRIORITY: Modular Architecture Refactoring**
  - Split scheduler.py (788 lines) into focused modules:
    - `core/scheduler.py` - Main scheduling logic
    - `core/site_checker.py` - Individual site checking
    - `core/content_fetcher.py` - Content fetching and extraction
    - `core/entity_processor.py` - Entity recognition and processing
    - `core/report_generator.py` - Report generation
    - `core/data_manager.py` - Data persistence and cleanup
  - Create `utils/` directory for shared utilities
  - Implement proper dependency injection
  - Add configuration validation module
  - Create plugin architecture for extensibility

## Security & Resilience
- [ ] **URL Security & Validation**
  - Implement comprehensive URL filtering system
  - Add whitelist/blacklist for TLDs, domains, and paths
  - Add protection against malicious URLs and DNS attacks
  - Implement OWASP URL validation checks
  - Add rate limiting per domain
  - Implement content size limits and timeout protections

- [ ] **Failure Tracking & Blacklisting**
  - Track failure counts per domain over time
  - Blacklist domains/paths after repeated failures (N failures over M days)
  - Implement exponential backoff for failed domains
  - Alert on suspicious failure patterns (potential attacks)
  - Add circuit breaker pattern for unreliable sites

- [ ] **Content Security**
  - Add content sanitization and validation
  - Implement protection against injection attacks
  - Add virus/malware scanning for downloaded content
  - Validate content types and sizes
  - Implement content integrity checks

## Error Handling & Monitoring
- [ ] **Robust Error Handling**
  - Ensure no URL access or content processing errors exit the program
  - Implement graceful degradation for all failure modes
  - Add comprehensive logging for all error conditions
  - Create error categorization and reporting system

- [ ] **Operational Monitoring**
  - Add health check endpoints for monitoring
  - Implement metrics collection (success rates, response times)
  - Add alerting for system health issues
  - Create operational dashboard
  - Add performance monitoring and profiling

## Code Organization
- [ ] Split scheduler.py into smaller, more focused modules
- [ ] Create a dedicated tests directory structure:
  ```
  tests/
  ├── unit/
  │   ├── test_fetcher.py
  │   ├── test_config.py
  │   └── test_utils.py
  ├── integration/
  │   ├── test_scheduler.py
  │   └── test_main_api.py
  └── e2e/
      └── test_end_to_end.py
  ```

## Documentation
- [ ] Create comprehensive API documentation
- [ ] Add more detailed installation and deployment instructions
- [ ] Document configuration options and their effects
- [ ] Update project workflow documentation
  - Review and update design documentation
  - Document versioning strategy
  - Define merge approaches

## Features
- [ ] Add support for more data retention policies
- [ ] Implement better error handling and recovery
- [ ] Add more comprehensive logging
- [ ] Improve test coverage for edge cases

## Performance
- [ ] Implement caching for frequently accessed data
- [ ] Optimize text processing pipelines
- [ ] Add rate limiting for external API calls

## Security
- [ ] Add input validation for all user-provided data
- [ ] Implement proper error handling for sensitive operations
- [ ] Add security headers to API responses

## Version Control
- [ ] Implement frequent versioning strategy
- [ ] Define merge approaches
  - Feature branches vs. trunk-based development
  - Pull request review process
  - Release branching strategy
- [ ] Document version control workflow
  - Commit message guidelines
  - Branch naming conventions
  - Merge conflict resolution process

## Automated Operations & Validation

### Phase 1: Automated Testing & Validation
- [ ] **Comprehensive Test Suite**
  - Unit tests for all core modules (target: 90% coverage)
  - Integration tests for API endpoints
  - End-to-end tests for complete workflows
  - Performance tests for large-scale operations
  - Security tests for vulnerability scanning

- [ ] **Automated Quality Assurance**
  - Set up continuous integration (GitHub Actions/Jenkins)
  - Automated code quality checks (flake8, mypy, bandit)
  - Automated security scanning (safety, semgrep)
  - Automated dependency vulnerability scanning
  - Performance regression testing

- [ ] **Configuration Validation**
  - Schema validation for all configuration files
  - Automated configuration testing
  - Environment-specific configuration validation
  - Configuration drift detection

### Phase 2: Automated Deployment & Operations
- [ ] **Containerization & Deployment**
  - Create Docker containers for all components
  - Set up container orchestration (Docker Compose/Kubernetes)
  - Implement blue-green deployment strategy
  - Add automated rollback capabilities

- [ ] **Monitoring & Alerting**
  - Set up automated health monitoring
  - Implement log aggregation and analysis
  - Create automated alerting for failures
  - Add performance monitoring and alerting
  - Implement automated incident response

- [ ] **Data Management Automation**
  - Automated backup and restore procedures
  - Automated data retention policy enforcement
  - Automated data integrity checks
  - Automated cleanup of temporary files and logs

### Phase 3: Manual Validation & Operations
- [ ] **Manual Testing Procedures**
  - Create manual testing checklists
  - Document manual validation procedures
  - Create troubleshooting guides
  - Document manual recovery procedures

- [ ] **Operational Procedures**
  - Create operational runbooks
  - Document manual intervention procedures
  - Create escalation procedures
  - Document maintenance procedures

- [ ] **Security Reviews**
  - Regular manual security audits
  - Penetration testing procedures
  - Code review guidelines
  - Security incident response procedures
