
"""Shared pytest fixtures for isolated database tests."""

from pathlib import Path

import duckdb
import pandas as pd
import pytest

from app.etl import load_orders


ROOT = Path(__file__).resolve().parents[1]
VIEWS_SQL = ROOT / "sql" / "views.sql"


@pytest.fixture
def test_db(tmp_path: Path) -> Path:
    """Build an isolated DuckDB database for each test."""

    csv_path = tmp_path / "orders.csv"
    db_path = tmp_path / "test_sales.duckdb"

    # Deterministic dataset with 10 customers.
    customers = [
        "Cliente_060",
        *[f"Cliente_{i:03d}" for i in range(1, 10)],
    ]

    amounts = [9517.90] + [100.0] * 9

    orders = pd.DataFrame({
        "pedido_id": range(1, 11),
        "fecha": ["2025-03-15"] * 10,
        "cliente": customers,
        "pais": ["España"] * 10,
        "producto": ["Producto_A"] * 10,
        "importe": amounts,
        "estado": ["completado"] * 10,
    })

    orders.to_csv(csv_path, index=False)

    # Reuse the actual application ETL.
    load_orders(
        csv_path=csv_path,
        db_path=db_path,
    )

    # Create analytical views.
    with duckdb.connect(str(db_path)) as conn:
        conn.execute(
            VIEWS_SQL.read_text(encoding="utf-8")
        )

    return db_path
