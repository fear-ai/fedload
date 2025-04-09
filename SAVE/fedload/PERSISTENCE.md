# 🗃 Persistence and Database Options

## CSV Output
Current output is saved to a CSV via `pandas.to_csv`. This is ideal for flat tabular data and portable export.

## SQLite
For local storage with query capability:
- Use `sqlite3` module (built-in)
- Convert scraped data into a table
- Supports indexing, joins, long-term archival

## PostgreSQL / MySQL
Use for:
- Multi-user access
- Remote/production storage
- Advanced queries

Libraries:
```bash
pip install sqlalchemy psycopg2-binary
```

## NoSQL (MongoDB)
Use when:
- Schema is flexible
- You store full HTML chunks or nested metadata

Library:
```bash
pip install pymongo
```

## Recommendation
Start with CSV or SQLite for dev/test. Use PostgreSQL or MongoDB in production if scaling.
