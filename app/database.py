
"""Secure read-only access to DuckDB."""

from pathlib import Path

import duckdb

from app.sql_validator import validate_sql


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "sales.duckdb"

MAX_ROWS = 100


class DatabaseQueryError(Exception):
    """Raised when database query validation fails."""


def execute_query(sql: str) -> list[dict]:
    """Validate and execute an analytical SQL query."""

    # 1. Validate SQL structure and allowed tables.
    validated_sql = validate_sql(sql)

    if not DB_PATH.exists():
        raise DatabaseQueryError(
            "DuckDB database not found."
        )

    try:
        # 2. Open database in read-only mode.
        with duckdb.connect(
            str(DB_PATH),
            read_only=True,
        ) as conn:

            # 3. Verify SQL semantics without executing it.
            # This catches unknown columns, for example.
            conn.execute(
                f"EXPLAIN {validated_sql}"
            )

            # 4. Limit the returned result set.
            limited_sql = (
                f"SELECT * FROM ({validated_sql}) "
                f"AS validated_result LIMIT {MAX_ROWS}"
            )

            # 5. Execute the validated query.
            cursor = conn.execute(limited_sql)

            columns = [
                column[0]
                for column in cursor.description
            ]

            rows = cursor.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]

    except duckdb.Error as exc:
        raise DatabaseQueryError(
            "Database query could not be executed."
        ) from exc
