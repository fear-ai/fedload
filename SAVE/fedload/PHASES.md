# 📌 Fed Load Project Phases

Each phase is modular and prompt-friendly for code generation or automation.

## Phase 1: Prototype
- Define a minimal script to extract links from a Federal Reserve webpage
- Use `requests` and `BeautifulSoup` to fetch and parse
- Output results to CSV

## Phase 2: Refactor
- Extract config handling into a layered system (defaults, file, env, CLI)
- Modularize: split into `main.py`, `config.py`, `loader.py`, `parser.py`

## Phase 3: Test
- Add unit tests for core functions (e.g. `parse_links`)
- Create scenario-driven test cases (malformed HTML, large files, edge cases)

## Phase 4: Tooling
- Add `requirements.txt`, `.gitignore`, VSCode launch/test config
- Create Jupyter workbooks for interactive dev and metrics

## Phase 5: Docs & Deploy
- Add `README.md`, `DEPLOY.md`, `PERSISTENCE.md`, `PHASES.md`
- Finalize ZIP packaging and GitHub-friendly structure
