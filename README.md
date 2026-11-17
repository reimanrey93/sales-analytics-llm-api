# Sales Analytics LLM API

Prueba técnica de Analytic Engineer. **Estado: etapa 1 (generación y ETL)**.

## Requisitos

Python 3.11 o superior.

## Instalación (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Generar, limpiar y cargar datos

```powershell
python scripts/generate_data.py
python -m app.etl
python -m pytest -q tests/test_etl.py
```

La generación utiliza una semilla fija. Produce 1.230 filas: 1.200 pedidos originales, 30 duplicados, 20 fechas inválidas y 25 importes vacíos (en registros diferentes). La política ETL elimina los duplicados por `pedido_id` y descarta filas con fecha o importe inválidos; no inventa importes. Resultado esperado: 1.155 pedidos limpios.

Se crea `data/sales.duckdb` localmente. El archivo de base de datos y el CSV generado están excluidos de Git por ser derivados reproducibles.

## En desarrollo

- Vistas SQL mensuales y clientes top 10.
- Endpoint FastAPI con LLM y validación SQL de solo lectura.
- Tests completos de seguridad y endpoint con mock del LLM.
- Decisiones, evolución y registro de uso de IA.
