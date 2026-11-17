# Sales Analytics LLM API

A Python sales analytics application that combines data engineering, DuckDB, FastAPI, and Google Gemini to answer natural-language questions through validated SQL queries.

Developed as a technical assessment for a Python / Analytic Engineer position.

## Architecture

```text
Natural-language question
          |
          v
    FastAPI POST /ask
          |
          v
  Google Gemini (NL-to-SQL)
          |
          v
   SQLGlot validation
          |
          v
 Read-only SQL execution
          |
          v
        DuckDB
     /         \
 Clean orders   Analytical views
     ^
     |
 Pandas ETL pipeline
 - Remove duplicate orders
 - Validate dates
 - Remove invalid or missing amounts
     ^
     |
 Synthetic orders CSV
```

The language model generates a candidate query; the application validates and executes it against actual database records.

## Technology Stack

- **Python 3.12** — application language
- **Pandas** — data cleaning and transformation
- **DuckDB** — embedded analytical database and SQL views
- **FastAPI / Pydantic** — REST API and request validation
- **Google Gemini** — natural-language-to-SQL generation
- **SQLGlot** — SQL parsing and structural validation
- **Pytest** — automated tests

## Project Structure

```text
app/
  main.py             # FastAPI application
  llm.py              # Gemini integration
  sql_validator.py    # SQL validation
  database.py         # Read-only DuckDB execution
  etl.py              # Data cleaning and loading

scripts/
  generate_data.py    # Synthetic orders generator
  create_views.py     # Analytical views creation

sql/
  views.sql

tests/
  conftest.py         # Isolated temporary DuckDB fixtures
  test_api.py
  test_etl.py
  test_sql_validator.py
  test_views.py

data/                 # Locally generated data (not committed)
.env.example
.gitignore
requirements.txt
README.md
```

## Installation

**Requirements:** Python 3.11+ and Git. The project was developed and tested with Python 3.12.

Clone the repository:

```bash
git clone https://github.com/reimanrey93/sales-analytics-llm-api.git
cd sales-analytics-llm-api
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run the following and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Dataset Generation and ETL

Generate the reproducible synthetic dataset:

```bash
python scripts/generate_data.py
```

The resulting `data/orders_raw.csv` contains **1,230 records**: 1,200 initial orders and 30 intentionally duplicated records. Among the original orders, 20 dates are invalid and 25 amounts are missing.

Clean and load the dataset into DuckDB:

```bash
python -m app.etl
```

The ETL removes duplicate order IDs, invalid dates, and missing or invalid amounts. It also rejects negative amounts. For the generated dataset, the expected result is:

| Metric | Rows |
|---|---:|
| Input records | 1,230 |
| Duplicate orders removed | 30 |
| Invalid dates removed | 20 |
| Missing or invalid amounts removed | 25 |
| Clean records | **1,155** |

The output is stored in `data/sales.duckdb`, in a table named `pedidos`. Missing financial values are excluded rather than imputed to avoid introducing artificial revenue.

## Analytical SQL Views

Create the views after running the ETL:

```bash
python scripts/create_views.py
```

The application provides two views:

| View | Description |
|---|---|
| `ventas_mensuales_pais` | Monthly sales and order counts by country |
| `top_10_clientes` | Ten customers with the highest total purchases |

Only orders with `estado = 'completado'` contribute to these sales metrics.

## Gemini Configuration

Copy `.env.example` to `.env` and set your own API key:

```dotenv
GEMINI_API_KEY=your_private_api_key
GEMINI_MODEL=gemini-3.8-flash
```

Create a key in [Google AI Studio](https://aistudio.google.com/api-keys). Model availability and API usage limits depend on your account.

**Never commit your real API key.** The `.env` file is excluded by `.gitignore`. A Gemini key is needed for live `/ask` requests, but not for the automated tests, which mock the LLM.

## Running the API

From the project root, after generating the dataset and creating the views:

```bash
python -m uvicorn app.main:app --reload
```

Open the interactive documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

**Health check:** `GET /health`

**Natural-language analytics:** `POST /ask`

Example JSON request:

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

The API returns the original question, generated SQL, retrieved rows, and row count. Numerical results come from DuckDB, not from LLM-generated estimates.

## SQL Validation and Safety

The LLM does not execute SQL directly. Candidate queries are parsed with SQLGlot and checked before being submitted to DuckDB.

The current implementation:

- Accepts a single `SELECT` statement only.
- Allows access only to `pedidos`, `ventas_mensuales_pais`, and `top_10_clientes`.
- Rejects joins, subqueries, common table expressions, and unsupported SQL functions.
- Rejects data-modification statements and arbitrary table-valued file access.
- Opens DuckDB in read-only mode.
- Uses `EXPLAIN` to detect invalid references before execution.
- Returns at most 100 rows per request.

Invalid or rejected SQL produces an HTTP `400` response; LLM generation failures produce HTTP `503`.

These safeguards are appropriate to the assessment scope, but do not constitute a complete production-grade query sandbox.

## Automated Tests

Run the test suite directly after installing dependencies:

```bash
python -m pytest -v
```

The tests use isolated temporary DuckDB databases and mocked LLM responses, so they do **not** require the generated local dataset, a running API server, or a Gemini API key.

Coverage includes data cleaning, analytical SQL views, accepted and rejected SQL, the FastAPI health endpoint, successful requests with a mocked LLM, and error handling.

**Latest local verification: 16 tests passed.**

## Technical Decisions

**Why DuckDB?** It provides fast analytical SQL without a separate database server, keeping local setup simple and reproducible.

**Why SQLGlot?** Structural parsing is more reliable than checking generated SQL through keyword-based string filters alone.

**Why separate the LLM and database layers?** Gemini generates candidate SQL, while the application controls validation and execution. This separation improves testability and limits direct LLM access to the database.

**Why discard invalid financial records?** Missing or invalid amounts cannot be reliably reconstructed; excluding them avoids fabricating sales values.

## Future Improvements

Given additional development time, I would focus on:

- Adding query execution timeouts and resource limits.
- Expanding SQL validation and automated security tests.
- Containerizing the application and adding CI/CD.

## AI-Assisted Development

**Tools:** OpenAI Codex (VS Code) and ChatGPT.

AI tools supported architecture design, Python development, SQL generation, debugging, testing, and documentation.

- **Requested:** Assistance with the ETL pipeline, FastAPI and Gemini integration, SQL validation, and automated tests.
- **Accepted:** Modular architecture, DuckDB analytical views, SQLGlot-based validation, and mocked LLM tests.
- **Corrected:** Gemini model compatibility, incomplete SQL generation, dependency configuration, and test isolation.

Changes were verified through local execution, automated tests, and incremental Git commits.

## Author

Reiman Alfonso Azcuy  
GitHub: [reimanrey93](https://github.com/reimanrey93)
