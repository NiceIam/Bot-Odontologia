-- Schema SQL para sistema de citas odontológicas
-- Ejecutar en PostgreSQL existente

-- Tabla de pacientes
CREATE TABLE IF NOT EXISTS pacientes (
    id SERIAL PRIMARY KEY,
    telefono VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100),
    email VARCHAR(100),
    fecha_nacimiento DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de doctores
CREATE TABLE IF NOT EXISTS doctores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    especialidad VARCHAR(100),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de servicios
CREATE TABLE IF NOT EXISTS servicios (
    id SERIAL PRIMARY KEY,
    categoria VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    duracion_minutos INTEGER NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de citas (actualizada con doctor y servicio)
CREATE TABLE IF NOT EXISTS citas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    doctor_id INTEGER NOT NULL REFERENCES doctores(id) ON DELETE CASCADE,
    servicio_id INTEGER NOT NULL REFERENCES servicios(id) ON DELETE CASCADE,
    fecha_hora TIMESTAMP NOT NULL,
    estado VARCHAR(20) DEFAULT 'agendada' CHECK (estado IN ('agendada', 'cancelada', 'completada', 'reagendada')),
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doctor_id, fecha_hora)
);

-- Tabla de estado de conversación
CREATE TABLE IF NOT EXISTS conversaciones (
    id SERIAL PRIMARY KEY,
    telefono VARCHAR(20) UNIQUE NOT NULL,
    estado VARCHAR(50) NOT NULL,
    contexto JSONB DEFAULT '{}',
    ultima_interaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_citas_paciente ON citas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_citas_doctor ON citas(doctor_id);
CREATE INDEX IF NOT EXISTS idx_citas_servicio ON citas(servicio_id);
CREATE INDEX IF NOT EXISTS idx_citas_fecha ON citas(fecha_hora);
CREATE INDEX IF NOT EXISTS idx_citas_estado ON citas(estado);
CREATE INDEX IF NOT EXISTS idx_conversaciones_telefono ON conversaciones(telefono);
CREATE INDEX IF NOT EXISTS idx_pacientes_telefono ON pacientes(telefono);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_pacientes_updated_at BEFORE UPDATE ON pacientes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_doctores_updated_at BEFORE UPDATE ON doctores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_servicios_updated_at BEFORE UPDATE ON servicios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_citas_updated_at BEFORE UPDATE ON citas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insertar doctores de prueba
INSERT INTO doctores (nombre, especialidad, activo) VALUES
('Dr. Juan Pérez', 'Ortodoncia', true),
('Dra. María González', 'Odontología General', true),
('Dr. Carlos Rodríguez', 'Cirugía Maxilofacial', true)
ON CONFLICT DO NOTHING;

-- Insertar catálogo de servicios
INSERT INTO servicios (categoria, nombre, duracion_minutos, activo) VALUES
-- Ortodoncia
('Ortodoncia', 'Valoración de Ortodoncia', 30, true),
('Ortodoncia', 'Control de Ortodoncia', 30, true),
('Ortodoncia', 'Montaje de Brackets', 60, true),

-- Ortopedia Maxilar
('Ortopedia Maxilar', 'Valoración de Ortopedia', 30, true),
('Ortopedia Maxilar', 'Procedimiento de Ortopedia', 60, true),

-- Odontología General
('Odontología General', 'Valoración General', 30, true),
('Odontología General', 'Procedimiento General', 60, true),

-- Odontología Estética
('Odontología Estética', 'Valoración Estética', 30, true),
('Odontología Estética', 'Procedimiento Estético', 60, true),

-- Blanqueamiento
('Blanqueamiento', 'Blanqueamiento Dental', 30, true),

-- Diseño de Sonrisa
('Diseño de Sonrisa', 'Valoración de Diseño de Sonrisa', 30, true),
('Diseño de Sonrisa', 'Diseño de Sonrisa', 60, true),

-- Rehabilitación Oral
('Rehabilitación Oral', 'Valoración de Rehabilitación', 30, true),
('Rehabilitación Oral', 'Procedimiento de Rehabilitación', 60, true),

-- Periodoncia
('Periodoncia', 'Valoración de Periodoncia', 30, true),
('Periodoncia', 'Procedimiento de Periodoncia', 60, true),

-- Profilaxis
('Profilaxis', 'Profilaxis Dental', 30, true)
ON CONFLICT DO NOTHING;

-- Comentarios
COMMENT ON TABLE citas IS 'Horario de atención: Lunes a Viernes, 8:00 - 17:00. Almuerzo: 12:00 - 13:00.';
COMMENT ON TABLE doctores IS 'Doctores disponibles en la clínica';
COMMENT ON TABLE servicios IS 'Catálogo de servicios odontológicos';
