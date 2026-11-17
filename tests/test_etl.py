import pandas as pd
from app.etl import clean_orders


def test_clean_orders_removes_duplicate_invalid_date_and_missing_amount():
    data = pd.DataFrame([
        {'pedido_id': 1, 'fecha': '2025-03-01', 'cliente': 'A', 'pais': 'España', 'producto': 'Mouse', 'importe': '20', 'estado': 'completado'},
        {'pedido_id': 1, 'fecha': '2025-03-01', 'cliente': 'A', 'pais': 'España', 'producto': 'Mouse', 'importe': '20', 'estado': 'completado'},
        {'pedido_id': 2, 'fecha': 'mal', 'cliente': 'B', 'pais': 'Chile', 'producto': 'Mouse', 'importe': '30', 'estado': 'completado'},
        {'pedido_id': 3, 'fecha': '2025-03-01', 'cliente': 'C', 'pais': 'Chile', 'producto': 'Mouse', 'importe': '', 'estado': 'completado'},
    ])
    result, stats = clean_orders(data)
    assert len(result) == 1
    assert result.iloc[0]['pedido_id'] == 1
    assert stats['duplicados'] == 1
    assert stats['fechas_invalidas'] == 1
    assert stats['importes_vacios_o_invalidos'] == 1
