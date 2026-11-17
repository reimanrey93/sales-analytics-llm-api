
import pytest

from app.sql_validator import (
    validate_sql,
    SQLValidationError,
)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM top_10_clientes",
        "SELECT SUM(importe) FROM pedidos",
        "SELECT pais, SUM(ventas_totales) "
        "FROM ventas_mensuales_pais GROUP BY pais",
    ],
)
def test_valid_queries(sql):
    assert validate_sql(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM pedidos",
        "DROP TABLE pedidos",
        "SELECT * FROM usuarios",
        "SELECT * FROM pedidos; DROP TABLE pedidos",
        "SELECT * FROM read_csv('/tmp/data.csv')",
        "SELECT * FROM pedidos JOIN usuarios USING (cliente)",
    ],
)
def test_unsafe_queries(sql):
    with pytest.raises(SQLValidationError):
        validate_sql(sql)


def test_invalid_syntax():
    with pytest.raises(SQLValidationError):
        validate_sql(
            "SELECT FROM"
        )
