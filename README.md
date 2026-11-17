
# Sales Analytics LLM API

A Python-based sales analytics application combining data engineering,
DuckDB, FastAPI, and Google Gemini to answer natural-language questions
using dynamically generated SQL queries.

Developed as a technical assessment for a Python / Analytic Engineer position.

## Architecture

```text
Synthetic Orders CSV
        |
        v
  Pandas ETL Pipeline
  - Remove duplicates
  - Validate dates
  - Handle missing amounts
        |
        v
      DuckDB
  - Clean orders
  - Monthly sales view
  - Top 10 customers view
        ^
        |
  Read-only SQL execution
        ^
        |
  SQLGlot validation
        ^
        |
  Google Gemini (NL-to-SQL)
        ^
        |
  FastAPI POST /ask
        ^
        |
  Natural-language question
```

## Technology Stack

- Python 3.12
- Pandas for data processing
- DuckDB for analytical storage and SQL views
- FastAPI and Pydantic for the REST API
- Google Gemini for natural-language-to-SQL generation
- SQLGlot for SQL parsing and validation
- Pytest for automated testing

## Project Structure

```text
app/
  main.py           # FastAPI application
  llm.py            # Gemini integration
  sql_validator.py  # SQL validation
  database.py       # Read-only DuckDB execution
  etl.py            # Data cleaning and loading

scripts/
  generate_data.py  # Synthetic data generator
  create_views.py   # Analytical views

sql/
  views.sql

tests/
  test_api.py
  test_etl.py
  test_sql_validator.py
  test_views.py

data/                # Generated locally
.env.example
.gitignore
requirements.txt
README.md
```

## Installation

Requirements: Python 3.11+ and Git.

Clone the repository:

```bash
git clone https://github.com/reimanrey93/sales-analytics-llm-api.git
cd sales-analytics-llm-api
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Dataset Generation

Generate synthetic orders:

```bash
python scripts/generate_data.py
```

The generated CSV contains 1,230 records:

- 1,200 original orders
- 30 duplicate records
- 20 invalid dates
- 25 missing amounts

The generator uses a fixed random seed for reproducibility.

## ETL Pipeline

Run:

```bash
python -m app.etl
```

The pipeline removes duplicate orders, invalid dates and
records with missing or invalid amounts.

Expected result:

- Original rows: 1,230
- Duplicates removed: 30
- Invalid dates removed: 20
- Invalid or missing amounts removed: 25
- Clean rows: 1,155

The cleaned records are stored in `data/sales.duckdb`.

Missing amounts are not artificially imputed because doing so
could distort financial aggregations.

## Analytical SQL Views

Create the views:

```bash
python scripts/create_views.py
```

The application provides:

1. `ventas_mensuales_pais`: monthly sales by country.
2. `top_10_clientes`: the ten highest-spending customers.

Only completed orders contribute to sales calculations.

## Gemini Configuration

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_private_api_key
GEMINI_MODEL=gemini-3.8-flash
```

Obtain a key from Google AI Studio:

https://aistudio.google.com/api-keys

API access and pricing depend on the selected model and account.

Never commit real API keys. The `.env` file is excluded from Git.

## Running the API

After generating the dataset and creating the views:

```bash
python -m uvicorn app.main:app --reload
```

Interactive API documentation:

http://127.0.0.1:8000/docs

Health check:

GET /health

Natural-language analytics:

POST /ask

Example request:

```json
{
  "question": "¿Cuáles son los 10 clientes que más compraron?"
}
```

Example generated SQL:

```sql
SELECT cliente, total_comprado
FROM top_10_clientes
ORDER BY total_comprado DESC
LIMIT 10;
```

The API returns the question, generated SQL, rows retrieved
from DuckDB, and the number of returned rows.

Responses contain database results rather than numerical
answers invented by the language model.

## SQL Validation and Safety

The LLM does not execute SQL directly.

SQLGlot inspects the generated SQL before execution.

Current restrictions include:

- Single SELECT statement only
- Explicit allowlist of database relations
- No INSERT, UPDATE, DELETE or DDL
- No joins, CTEs or subqueries
- Restricted SQL functions
- No arbitrary table-valued file access
- DuckDB connection opened in read-only mode
- Database schema validation using EXPLAIN
- Maximum of 100 returned rows

Invalid SQL returns an HTTP 400 response.
LLM generation failures return HTTP 503.

These controls reduce risk but are not a complete
production-grade sandbox.

## Automated Tests

After preparing the local database and SQL views, run:

```bash
python -m pytest -v
```

The implemented test suite covers:

- Data cleaning
- Analytical SQL views
- Valid SQL queries
- Destructive or unauthorized SQL
- FastAPI health endpoint
- API execution with a mocked LLM
- LLM error handling

Latest local verification: 16 tests passed.

The mocked LLM tests do not consume Gemini API quota.

## Technical Decisions

### Why DuckDB?

DuckDB is lightweight, embedded, and optimized for analytical
SQL workloads. It eliminates the need for an external database
server while remaining suitable for this small assessment.

### Why SQLGlot?

The application parses SQL structurally rather than attempting
to block malicious statements through keyword matching alone.

### Why separate the LLM and database layers?

The language model generates candidate SQL. The application
is responsible for validation and execution. This separation
makes the system easier to test and maintain.

### Why discard invalid financial records?

Missing amounts cannot be reliably inferred. Discarding
invalid records avoids introducing fabricated sales values.

## Limitations and Future Improvements

With more development time, I would:

1. Make every test fully independent of pre-generated files.
2. Introduce query execution timeouts and resource limits.
3. Strengthen SQL function and column-level allowlists.
4. Add structured logs, metrics and request tracing.
5. Add pagination for larger query results.
6. Containerize the application using Docker.
7. Add continuous integration with GitHub Actions.
8. Support alternative LLM providers behind a common interface.
9. Evaluate cloud deployment and managed analytical storage.

## AI-Assisted Development

AI tools were used as development assistance, not as a
substitute for testing or technical validation.

Tool used: ChatGPT.

### What I asked AI to help with

- Initial project architecture and module decomposition
- Pandas ETL implementation
- DuckDB analytical SQL views
- FastAPI and Gemini integration
- SQLGlot validation strategies
- Automated test examples
- Documentation structure

### What I accepted

- Modular separation between ETL, LLM, validation and API
- Synthetic dataset generation
- Use of DuckDB for local analytics
- FastAPI request validation
- Pytest with a mocked LLM
- Explicit allowlisting of SQL relations

### What I corrected or verified

- Replaced the initially proposed LLM model after an API error
- Increased generation output limits after truncated SQL
- Added checks for incomplete LLM generation
- Corrected a test confusing SQL syntax with column existence
- Added database-level schema verification using EXPLAIN
- Corrected the dependency list
- Removed a credential from an unpublished Git commit
- Verified API responses against actual DuckDB records

Each development stage was tested and committed separately.

## Development History

The Git history records the progressive implementation of:

1. Synthetic dataset generation and ETL
2. Analytical SQL views
3. FastAPI and Gemini integration
4. SQL validation and read-only database execution
5. Final documentation and reproducibility improvements

## Author

Reiman Alfonso Azcuy

GitHub: https://github.com/reimanrey93
