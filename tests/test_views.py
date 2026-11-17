
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "sales.duckdb"
SQL_PATH = ROOT / "sql" / "views.sql"


def test_analytical_views():
    assert DB_PATH.exists(), "Run ETL before testing views"

    with duckdb.connect(str(DB_PATH), read_only=True) as conn:
        monthly = conn.execute(
            "SELECT COUNT(*) FROM ventas_mensuales_pais"
        ).fetchone()[0]

        customers = conn.execute(
            "SELECT COUNT(*) FROM top_10_clientes"
        ).fetchone()[0]

        assert monthly > 0
        assert customers == 10

        # Check that the ranking is descending.
        amounts = [
            row[0]
            for row in conn.execute(
                "SELECT total_comprado FROM top_10_clientes "
                "ORDER BY total_comprado DESC"
            ).fetchall()
        ]

        assert amounts == sorted(amounts, reverse=True)
