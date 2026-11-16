CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    ci VARCHAR(20) NOT NULL,
    saldo NUMERIC(10,2) NOT NULL,
    rol VARCHAR(20) DEFAULT 'cliente'
);

CREATE TABLE IF NOT EXISTS transferencias (
    id SERIAL PRIMARY KEY,
    cuenta_origen INT NOT NULL,
    cuenta_destino INT NOT NULL,
    monto NUMERIC(10,2) NOT NULL,
    detalle TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS comentarios (
    id SERIAL PRIMARY KEY,
    autor VARCHAR(50) NOT NULL,
    mensaje TEXT NOT NULL
);

INSERT INTO usuarios (username, password_hash, nombre_completo, ci, saldo, rol) VALUES
('cmendoza', 'md5_inseguro_123', 'Carlos Mendoza', '4589211', 15400.00, 'cliente'),
('mortiz', 'md5_inseguro_456', 'Mariana Ortiz', '5892341', 3200.50, 'cliente'),
('admin_coop', 'admin_super_secret', 'Administrador General', '1002003', 99999.00, 'admin');

INSERT INTO comentarios (autor, mensaje) VALUES
('cmendoza', 'Excelente atención en la sucursal de Uriondo.'),
('mortiz', 'Consulta sobre el cobro mediante QR.');
