WITH TransaccionesAprobadas AS (
    SELECT 
        id_transaccion,
        id_cliente,
        fecha_hora,
        monto_usd,
        LAG(monto_usd) OVER (PARTITION BY id_cliente ORDER BY fecha_hora) AS monto_anterior
    FROM 
        transacciones
    WHERE 
        estado_transaccion = 'aprobada'
)
SELECT 
    id_cliente,
    id_transaccion,
    fecha_hora,
    monto_usd AS monto_actual,
    monto_anterior
FROM 
    TransaccionesAprobadas
WHERE 
    monto_anterior IS NOT NULL 
    AND monto_usd >= (monto_anterior * 5)
ORDER BY 
    id_cliente, 
    fecha_hora;