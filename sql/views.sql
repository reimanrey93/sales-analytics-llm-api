
-- Vista 1: ventas mensuales por país
-- Solo cuentan los pedidos completados.
CREATE OR REPLACE VIEW ventas_mensuales_pais AS
SELECT
    CAST(DATE_TRUNC('month', fecha) AS DATE) AS mes,
    pais,
    COUNT(*) AS total_pedidos,
    ROUND(SUM(importe), 2) AS ventas_totales
FROM pedidos
WHERE estado = 'completado'
GROUP BY 1, 2;

-- Vista 2: los 10 clientes con mayores compras
CREATE OR REPLACE VIEW top_10_clientes AS
SELECT
    cliente,
    COUNT(*) AS total_pedidos,
    ROUND(SUM(importe), 2) AS total_comprado
FROM pedidos
WHERE estado = 'completado'
GROUP BY cliente
ORDER BY total_comprado DESC, cliente ASC
LIMIT 10;
