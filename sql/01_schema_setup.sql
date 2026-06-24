-- Crear la tabla transacciones
CREATE TABLE transacciones (
    id_transaccion VARCHAR(50) PRIMARY KEY,
    id_cliente VARCHAR(50) NOT NULL,
    fecha_hora TIMESTAMP NOT NULL,
    monto_usd NUMERIC(10, 2), -- Permite nulos
    tipo_comercio VARCHAR(50) NOT NULL,
    estado_transaccion VARCHAR(50) NOT NULL,
    es_monto_inusual BOOLEAN NOT NULL
);

-- Crear índices para optimizar la consulta analítica de la Fase 2
CREATE INDEX idx_cliente_fecha ON transacciones(id_cliente, fecha_hora);
CREATE INDEX idx_estado ON transacciones(estado_transaccion);