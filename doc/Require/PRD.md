# Product Requirements Document (PRD) – FedLoad

## 1. Product Vision & Scope
FedLoad is a lightweight, modular system for monitoring US Federal Reserve websites, detecting content changes, extracting entities, and generating reports for analysts, researchers, and the public.

## 2. Features & User Stories
### Core Features (from README & requirements):
- Monitor all 12 district banks and key FED/FRB sites
- Detect and log content changes (HTML, PDF)
- Extract and persist named entities (people, organizations, publications)
- Generate daily and weekly HTML reports
- Provide REST API for querying status, entities, publications, and configuration
- Configurable scheduling, retention, and notification options

### User Stories
- As a financial analyst, I want to be notified of changes on FED sites so I can react quickly.
- As a researcher, I want to extract and analyze named entities from FED publications.
- As a journalist, I want to receive daily summaries of changes and new content.
- [OPEN] As a user, I want to export data in formats X, Y, Z (to be defined).

## 3. Acceptance Criteria
- System detects and logs changes on all configured sites
- Entities are extracted and stored in JSON
- Reports are generated and retained per configuration
- API endpoints are documented and functional
- [OPEN] Define performance, reliability, and usability criteria

## 4. Non-Functional Requirements
- Response time < 2 seconds for API requests
- Memory usage < 500MB
- Secure storage and input validation
- [OPEN] Accessibility, localization, or other requirements?

## 5. Out of Scope
- Real-time streaming or push notifications (currently)
- Deep learning-based entity extraction (currently)
- [OPEN] Any other exclusions?

## 6. Open Questions
- What export/integration formats are required by users?
- What are the most important performance and reliability metrics?
- [OPEN] Are there additional user roles or workflows to support? 