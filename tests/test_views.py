
"""Tests for DuckDB analytical views."""

import duckdb


def test_analytical_views(test_db):
    """Verify analytical views using an isolated database."""

    with duckdb.connect(
        str(test_db),
        read_only=True,
    ) as conn:

        monthly = conn.execute(
            "SELECT COUNT(*) FROM ventas_mensuales_pais"
        ).fetchone()[0]

        customers = conn.execute(
            "SELECT COUNT(*) FROM top_10_clientes"
        ).fetchone()[0]

        assert monthly > 0
        assert customers == 10

        amounts = [
            row[0]
            for row in conn.execute(
                "SELECT total_comprado "
                "FROM top_10_clientes "
                "ORDER BY total_comprado DESC"
            ).fetchall()
        ]

        assert amounts == sorted(
            amounts,
            reverse=True,
        )
