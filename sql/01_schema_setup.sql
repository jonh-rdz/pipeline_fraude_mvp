-- Crear la tabla transacciones asegurando idempotencia
CREATE TABLE IF NOT EXISTS transacciones (
    id_transaccion VARCHAR(50) PRIMARY KEY,
    id_cliente VARCHAR(50) NOT NULL,
    fecha_hora TIMESTAMP NOT NULL,
    monto_usd NUMERIC(10, 2),
    tipo_comercio VARCHAR(50) NOT NULL,
    estado_transaccion VARCHAR(50) NOT NULL,
    es_monto_inusual BOOLEAN NOT NULL
);

-- Crear índices garantizando que no generen error si ya existen
CREATE INDEX IF NOT EXISTS idx_cliente_fecha ON transacciones(id_cliente, fecha_hora);
CREATE INDEX IF NOT EXISTS idx_estado ON transacciones(estado_transaccion);

-- Deshabilitar seguridad para el entorno de pruebas MVP
ALTER TABLE transacciones DISABLE ROW LEVEL SECURITY;