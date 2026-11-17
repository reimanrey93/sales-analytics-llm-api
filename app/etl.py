"""Pipeline de limpieza de pedidos y carga a DuckDB."""
from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'orders_raw.csv'
DB = ROOT / 'data' / 'sales.duckdb'


def clean_orders(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    required = {'pedido_id', 'fecha', 'cliente', 'pais', 'producto', 'importe', 'estado'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f'Columnas faltantes: {sorted(missing)}')

    orders = df.copy()
    initial = len(orders)
    orders = orders.drop_duplicates(subset=['pedido_id'], keep='first').copy()
    duplicates = initial - len(orders)

    orders['fecha'] = pd.to_datetime(orders['fecha'], format='%Y-%m-%d', errors='coerce')
    bad_dates = int(orders['fecha'].isna().sum())
    orders = orders.dropna(subset=['fecha']).copy()

    orders['importe'] = pd.to_numeric(orders['importe'], errors='coerce')
    bad_amounts = int(orders['importe'].isna().sum())
    orders = orders.dropna(subset=['importe']).copy()

    # Los importes no negativos son un invariante del dataset sintético.
    negative_amounts = int((orders['importe'] < 0).sum())
    orders = orders.loc[orders['importe'] >= 0].copy()
    orders['pedido_id'] = pd.to_numeric(orders['pedido_id'], errors='raise').astype('int64')
    orders['fecha'] = orders['fecha'].dt.date
    orders = orders.sort_values('pedido_id').reset_index(drop=True)

    stats = {
        'filas_originales': initial,
        'duplicados': duplicates,
        'fechas_invalidas': bad_dates,
        'importes_vacios_o_invalidos': bad_amounts,
        'importes_negativos': negative_amounts,
        'filas_limpias': len(orders),
    }
    return orders, stats


def load_orders(csv_path: Path = RAW, db_path: Path = DB) -> dict[str, int]:
    if not csv_path.exists():
        raise FileNotFoundError(f'No existe {csv_path}. Ejecuta scripts/generate_data.py primero.')
    clean, stats = clean_orders(pd.read_csv(csv_path, dtype={'pedido_id': 'int64'}))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(db_path)) as conn:
        conn.register('clean_input', clean)
        conn.execute('CREATE OR REPLACE TABLE pedidos AS SELECT * FROM clean_input')
        conn.unregister('clean_input')
    return stats


if __name__ == '__main__':
    for key, value in load_orders().items():
        print(f'{key}: {value}')
