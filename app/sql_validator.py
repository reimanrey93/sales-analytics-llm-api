
"""Validate LLM-generated DuckDB SQL queries."""

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


ALLOWED_TABLES = {
    "pedidos",
    "ventas_mensuales_pais",
    "top_10_clientes",
}

ALLOWED_FUNCTIONS = {
    "SUM",
    "COUNT",
    "AVG",
    "MIN",
    "MAX",
    "ROUND",
    "DATE_TRUNC",
    "EXTRACT",
    "YEAR",
    "MONTH",
    "COALESCE",
    "CAST",
    "LOWER",
    "UPPER",
}

FORBIDDEN_EXPRESSIONS = (
    exp.Subquery,
    exp.CTE,
    exp.With,
    exp.Join,
    exp.Union,
    exp.Intersect,
    exp.Except,
    exp.Into,
)


class SQLValidationError(Exception):
    """Raised when SQL is unsafe or invalid."""


def validate_sql(sql: str) -> str:
    """Validate a single read-only SQL query."""

    if not sql or not sql.strip():
        raise SQLValidationError("Empty SQL query.")

    try:
        statements = sqlglot.parse(
            sql,
            read="duckdb",
            error_level="RAISE",
        )
    except (ParseError, ValueError) as exc:
        raise SQLValidationError(
            "Invalid SQL syntax."
        ) from exc

    if len(statements) != 1:
        raise SQLValidationError(
            "Only one SQL statement is allowed."
        )

    expression = statements[0]

    if not isinstance(expression, exp.Select):
        raise SQLValidationError(
            "Only SELECT queries are allowed."
        )

    for node in expression.walk():
        if isinstance(node, FORBIDDEN_EXPRESSIONS):
            raise SQLValidationError(
                "Unsupported or unsafe SQL structure."
            )

        if isinstance(node, exp.Func):
            name = (
                node.name
                if isinstance(node, exp.Anonymous)
                else node.sql_name()
            ).upper()

            if name not in ALLOWED_FUNCTIONS:
                raise SQLValidationError(
                    f"Function not allowed: {name}"
                )

    tables = list(expression.find_all(exp.Table))

    # First version: one authorized table or view.
    if len(tables) != 1:
        raise SQLValidationError(
            "Exactly one source table is required."
        )

    table = tables[0]

    if table.db or table.catalog:
        raise SQLValidationError(
            "Qualified table names are not allowed."
        )

    if table.name.lower() not in ALLOWED_TABLES:
        raise SQLValidationError(
            f"Table not allowed: {table.name}"
        )

    return expression.sql(dialect="duckdb")
