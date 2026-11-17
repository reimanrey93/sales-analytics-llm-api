
"""Create and verify analytical views in DuckDB."""

from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "sales.duckdb"
SQL_PATH = ROOT / "sql" / "views.sql"


def create_views():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            "Database not found. Run python -m app.etl first."
        )

    sql = SQL_PATH.read_text(encoding="utf-8")

    with duckdb.connect(str(DB_PATH)) as conn:
        conn.execute(sql)

        views = [
            "ventas_mensuales_pais",
            "top_10_clientes",
        ]

        for view in views:
            count = conn.execute(
                f"SELECT COUNT(*) FROM {view}"
            ).fetchone()[0]
            print(f"{view}: {count} filas")

        print("\nTop 10 clientes:")
        print(
            conn.execute(
                "SELECT * FROM top_10_clientes"
            ).df().to_string(index=False)
        )


if __name__ == "__main__":
    create_views()
