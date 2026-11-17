"""Genera pedidos sintéticos reproducibles con problemas de calidad deliberados."""
from pathlib import Path
import csv
import random
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'data' / 'orders_raw.csv'


def generate(path: Path = OUTPUT, seed: int = 42) -> Path:
    rng = random.Random(seed)
    countries = ['España', 'Argentina', 'México', 'Chile', 'Colombia']
    products = ['Notebook', 'Monitor', 'Teclado', 'Mouse', 'Auriculares']
    statuses = ['completado', 'pendiente', 'cancelado']
    rows = []
    start = date(2025, 1, 1)
    for i in range(1200):
        rows.append({
            'pedido_id': i + 1,
            'fecha': (start + timedelta(days=rng.randrange(365))).isoformat(),
            'cliente': f'Cliente_{rng.randrange(1, 101):03d}',
            'pais': rng.choice(countries),
            'producto': rng.choice(products),
            'importe': f'{rng.uniform(10, 1200):.2f}',
            'estado': rng.choices(statuses, weights=[75, 15, 10])[0],
        })

    # Errores en filas diferentes: 20 fechas inválidas y 25 importes vacíos.
    for i in range(20):
        rows[i]['fecha'] = '2025-99-99'
    for i in range(20, 45):
        rows[i]['importe'] = ''

    # 30 duplicados de pedidos existentes (mismo pedido_id y demás datos).
    rows.extend(dict(rows[i]) for i in range(45, 75))
    rng.shuffle(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f'Generado {path} ({len(rows)} filas)')
    return path


if __name__ == '__main__':
    generate()
