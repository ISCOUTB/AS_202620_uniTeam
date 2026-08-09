BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'rol_usuario') THEN
    CREATE TYPE rol_usuario AS ENUM ('SUPERADMIN', 'ADMIN', 'AUDITOR', 'CUSTODIO', 'TECNICO');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_activo') THEN
    CREATE TYPE estado_activo AS ENUM ('ACTIVO', 'MANTENIMIENTO', 'DESINCORPORADO', 'EN_TRASLADO', 'PERDIDO');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_traslado') THEN
    CREATE TYPE estado_traslado AS ENUM ('PENDIENTE', 'APROBADO', 'RECHAZADO', 'EN_TRANSITO', 'COMPLETADO', 'CANCELADO');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_movimiento_activo') THEN
    CREATE TYPE tipo_movimiento_activo AS ENUM ('TRASLADO', 'INVENTARIO', 'ASIGNACION', 'CAMBIO_ESTADO', 'MANTENIMIENTO', 'CREACION', 'ACTUALIZACION');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_sesion_inventario') THEN
    CREATE TYPE estado_sesion_inventario AS ENUM ('ABIERTA', 'EN_PROGRESO', 'CERRADA');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'resultado_escaneo_inventario') THEN
    CREATE TYPE resultado_escaneo_inventario AS ENUM ('ENCONTRADO', 'FALTANTE', 'EXTRA', 'UBICACION_INCORRECTA');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_documento') THEN
    CREATE TYPE tipo_documento AS ENUM ('FACTURA', 'GARANTIA', 'MANUAL', 'FOTO', 'OTRO');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'canal_notificacion') THEN
    CREATE TYPE canal_notificacion AS ENUM ('EN_APP', 'CORREO', 'PUSH', 'SMS');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'operacion_sincronizacion') THEN
    CREATE TYPE operacion_sincronizacion AS ENUM ('INSERTAR', 'ACTUALIZAR', 'ELIMINAR');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_sincronizacion') THEN
    CREATE TYPE estado_sincronizacion AS ENUM ('PENDIENTE', 'SINCRONIZADO', 'FALLIDO', 'CONFLICTO');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'prioridad_mantenimiento') THEN
    CREATE TYPE prioridad_mantenimiento AS ENUM ('BAJA', 'MEDIA', 'ALTA', 'CRITICA');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_mantenimiento') THEN
    CREATE TYPE estado_mantenimiento AS ENUM ('ABIERTA', 'EN_PROGRESO', 'COMPLETADA', 'CANCELADA');
  END IF;
END $$;

-- =========================
-- TABLAS MAESTRAS
-- =========================
CREATE TABLE IF NOT EXISTS departamentos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(255) NOT NULL,
  codigo VARCHAR(50) UNIQUE,
  esta_activo BOOLEAN NOT NULL DEFAULT true,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS usuarios (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  correo CITEXT UNIQUE NOT NULL,
  hash_contrasena TEXT NOT NULL,
  nombre_completo VARCHAR(255) NOT NULL,
  rol rol_usuario NOT NULL,
  departamento_id UUID REFERENCES departamentos(id) ON DELETE SET NULL,
  esta_activo BOOLEAN NOT NULL DEFAULT true,
  ultimo_inicio_sesion_en TIMESTAMPTZ,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ubicaciones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(255) NOT NULL,
  codigo VARCHAR(50) UNIQUE NOT NULL,
  edificio VARCHAR(100),
  piso VARCHAR(20),
  padre_id UUID REFERENCES ubicaciones(id) ON DELETE RESTRICT,
  esta_activo BOOLEAN NOT NULL DEFAULT true,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS categorias_activos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(255) NOT NULL,
  codigo VARCHAR(50) UNIQUE,
  anos_depreciacion INT CHECK (anos_depreciacion IS NULL OR anos_depreciacion > 0),
  intervalo_mantenimiento_dias INT CHECK (intervalo_mantenimiento_dias IS NULL OR intervalo_mantenimiento_dias > 0),
  padre_id UUID REFERENCES categorias_activos(id) ON DELETE RESTRICT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- ACTIVOS
-- =========================
CREATE TABLE IF NOT EXISTS activos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo VARCHAR(100) UNIQUE NOT NULL,
  codigo_qr TEXT,
  codigo_barras VARCHAR(100),
  etiqueta_rfid VARCHAR(100),
  nombre VARCHAR(255) NOT NULL,
  descripcion TEXT,
  marca VARCHAR(100),
  modelo VARCHAR(100),
  numero_serie VARCHAR(100),
  categoria_id UUID REFERENCES categorias_activos(id) ON DELETE RESTRICT,
  estado estado_activo NOT NULL DEFAULT 'ACTIVO',
  ubicacion_actual_id UUID REFERENCES ubicaciones(id) ON DELETE SET NULL,
  asignado_a_usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  fecha_adquisicion DATE,
  valor_adquisicion NUMERIC(15,2) CHECK (valor_adquisicion IS NULL OR valor_adquisicion >= 0),
  moneda VARCHAR(10) NOT NULL DEFAULT 'USD',
  proveedor VARCHAR(255),
  numero_factura VARCHAR(100),
  garantia_hasta DATE,
  url_imagen TEXT,
  notas TEXT,
  creado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  version INT NOT NULL DEFAULT 1,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  eliminado_en TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS documentos_activos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  activo_id UUID NOT NULL REFERENCES activos(id) ON DELETE CASCADE,
  tipo_documento tipo_documento NOT NULL,
  nombre_archivo VARCHAR(255) NOT NULL,
  url_archivo TEXT NOT NULL,
  tipo_mime VARCHAR(100),
  tamano_bytes BIGINT CHECK (tamano_bytes IS NULL OR tamano_bytes >= 0),
  subido_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- TRASLADOS Y AUDITORIA
-- =========================
CREATE TABLE IF NOT EXISTS traslados (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  numero_traslado VARCHAR(50) UNIQUE NOT NULL,
  activo_id UUID NOT NULL REFERENCES activos(id) ON DELETE RESTRICT,
  ubicacion_origen_id UUID REFERENCES ubicaciones(id) ON DELETE SET NULL,
  ubicacion_destino_id UUID NOT NULL REFERENCES ubicaciones(id) ON DELETE RESTRICT,
  usuario_origen_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  usuario_destino_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  motivo TEXT,
  estado estado_traslado NOT NULL DEFAULT 'PENDIENTE',
  solicitado_por UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
  aprobado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  aprobado_en TIMESTAMPTZ,
  motivo_rechazo TEXT,
  confirmado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  confirmado_en TIMESTAMPTZ,
  fecha_esperada DATE,
  completado_en TIMESTAMPTZ,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT chk_traslado_aprobacion
    CHECK (
      (estado <> 'APROBADO') OR
      (aprobado_por IS NOT NULL AND aprobado_en IS NOT NULL)
    ),

  CONSTRAINT chk_traslado_rechazo
    CHECK (
      (estado <> 'RECHAZADO') OR
      (motivo_rechazo IS NOT NULL)
    ),

  CONSTRAINT chk_traslado_completado
    CHECK (
      (estado <> 'COMPLETADO') OR
      (confirmado_por IS NOT NULL AND confirmado_en IS NOT NULL AND completado_en IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS movimientos_activos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  activo_id UUID NOT NULL REFERENCES activos(id) ON DELETE RESTRICT,
  tipo_movimiento tipo_movimiento_activo NOT NULL,
  ubicacion_desde_id UUID REFERENCES ubicaciones(id) ON DELETE SET NULL,
  ubicacion_hasta_id UUID REFERENCES ubicaciones(id) ON DELETE SET NULL,
  usuario_desde_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  usuario_hasta_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  estado_desde estado_activo,
  estado_hasta estado_activo,
  realizado_por UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
  traslado_id UUID REFERENCES traslados(id) ON DELETE SET NULL,
  notas TEXT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- INVENTARIO Y SINCRONIZACION OFFLINE
-- =========================
CREATE TABLE IF NOT EXISTS sesiones_inventario (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  numero_sesion VARCHAR(50) UNIQUE NOT NULL,
  ubicacion_id UUID NOT NULL REFERENCES ubicaciones(id) ON DELETE RESTRICT,
  estado estado_sesion_inventario NOT NULL DEFAULT 'ABIERTA',
  iniciado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  cerrado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  iniciado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  cerrado_en TIMESTAMPTZ,
  total_esperado INT NOT NULL DEFAULT 0,
  total_escaneado INT NOT NULL DEFAULT 0,
  total_encontrado INT NOT NULL DEFAULT 0,
  total_faltante INT NOT NULL DEFAULT 0,
  total_extra INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS items_inventario (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sesion_id UUID NOT NULL REFERENCES sesiones_inventario(id) ON DELETE CASCADE,
  activo_id UUID REFERENCES activos(id) ON DELETE SET NULL,
  codigo_escaneado VARCHAR(200),
  resultado_escaneo resultado_escaneo_inventario NOT NULL,
  ubicacion_esperada_id UUID REFERENCES ubicaciones(id) ON DELETE SET NULL,
  ubicacion_encontrada_id UUID REFERENCES ubicaciones(id) ON DELETE SET NULL,
  escaneado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  escaneado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  id_evento_cliente UUID,
  notas TEXT,

  CONSTRAINT chk_item_inventario_origen
    CHECK (activo_id IS NOT NULL OR codigo_escaneado IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS cola_sincronizacion (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dispositivo_id VARCHAR(100) NOT NULL,
  usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  nombre_entidad VARCHAR(100) NOT NULL,
  entidad_id UUID,
  operacion operacion_sincronizacion NOT NULL,
  payload JSONB NOT NULL,
  estado estado_sincronizacion NOT NULL DEFAULT 'PENDIENTE',
  reintentos INT NOT NULL DEFAULT 0,
  ultimo_error TEXT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  sincronizado_en TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS conflictos_sincronizacion (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cola_id UUID REFERENCES cola_sincronizacion(id) ON DELETE CASCADE,
  nombre_entidad VARCHAR(100) NOT NULL,
  entidad_id UUID,
  payload_cliente JSONB NOT NULL,
  payload_servidor JSONB NOT NULL,
  resuelto_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  resuelto_en TIMESTAMPTZ,
  notas_resolucion TEXT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- AUTENTICACION, NOTIFICACIONES, REPORTES E INTEGRACIONES
-- =========================
CREATE TABLE IF NOT EXISTS sesiones_autenticacion (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  hash_token_refresh TEXT NOT NULL,
  dispositivo_id VARCHAR(100),
  agente_usuario TEXT,
  direccion_ip INET,
  emitido_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expira_en TIMESTAMPTZ NOT NULL,
  revocado_en TIMESTAMPTZ,
  reemplazado_por UUID REFERENCES sesiones_autenticacion(id) ON DELETE SET NULL,
  UNIQUE (usuario_id, hash_token_refresh)
);

CREATE TABLE IF NOT EXISTS notificaciones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  tipo VARCHAR(100) NOT NULL,
  titulo VARCHAR(255) NOT NULL,
  mensaje TEXT,
  data JSONB,
  esta_leido BOOLEAN NOT NULL DEFAULT false,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  leido_en TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS entregas_notificacion (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  notificacion_id UUID NOT NULL REFERENCES notificaciones(id) ON DELETE CASCADE,
  canal canal_notificacion NOT NULL,
  id_externo VARCHAR(255),
  entregado_en TIMESTAMPTZ,
  fallido_en TIMESTAMPTZ,
  mensaje_error TEXT
);

CREATE TABLE IF NOT EXISTS exportaciones_reportes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  solicitado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  tipo_reporte VARCHAR(100) NOT NULL,
  formato_archivo VARCHAR(10) NOT NULL CHECK (formato_archivo IN ('PDF', 'XLSX', 'CSV')),
  filtros JSONB,
  estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'EJECUTANDO', 'FINALIZADO', 'FALLIDO')),
  url_archivo TEXT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finalizado_en TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS trabajos_integracion (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  proveedor VARCHAR(50) NOT NULL CHECK (proveedor IN ('SAP', 'ODOO', 'OTRO')),
  direccion VARCHAR(10) NOT NULL CHECK (direccion IN ('ENTRADA', 'SALIDA')),
  nombre_entidad VARCHAR(100) NOT NULL,
  payload JSONB,
  estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'EJECUTANDO', 'FINALIZADO', 'FALLIDO')),
  reintentos INT NOT NULL DEFAULT 0,
  mensaje_error TEXT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  procesado_en TIMESTAMPTZ
);

-- =========================
-- MANTENIMIENTO + SOPORTE IA
-- =========================
CREATE TABLE IF NOT EXISTS planes_mantenimiento (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  activo_id UUID NOT NULL REFERENCES activos(id) ON DELETE CASCADE,
  intervalo_dias INT NOT NULL CHECK (intervalo_dias > 0),
  proxima_fecha DATE,
  esta_activo BOOLEAN NOT NULL DEFAULT true,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ordenes_mantenimiento (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  activo_id UUID NOT NULL REFERENCES activos(id) ON DELETE RESTRICT,
  prioridad prioridad_mantenimiento NOT NULL DEFAULT 'MEDIA',
  estado estado_mantenimiento NOT NULL DEFAULT 'ABIERTA',
  titulo VARCHAR(255) NOT NULL,
  descripcion TEXT,
  programado_para TIMESTAMPTZ,
  abierto_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  asignado_a UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  cerrado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  abierto_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  cerrado_en TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS predicciones_ia (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  activo_id UUID NOT NULL REFERENCES activos(id) ON DELETE CASCADE,
  nombre_modelo VARCHAR(100) NOT NULL,
  tipo_prediccion VARCHAR(100) NOT NULL,
  puntaje NUMERIC(5,4) CHECK (puntaje IS NULL OR (puntaje >= 0 AND puntaje <= 1)),
  fecha_predicha DATE,
  detalle JSONB,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- FUNCIONES Y TRIGGERS
-- =========================
CREATE OR REPLACE FUNCTION fn_establecer_actualizado_en()
RETURNS TRIGGER AS $$
BEGIN
  NEW.actualizado_en = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_bloquear_cambio_inmutable()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'movimientos_activos es inmutable. No se permite UPDATE ni DELETE.';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_completar_traslado_aplicar_activo()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.estado = 'COMPLETADO' AND (OLD.estado IS DISTINCT FROM NEW.estado) THEN
    UPDATE activos
    SET
      ubicacion_actual_id = NEW.ubicacion_destino_id,
      asignado_a_usuario_id = COALESCE(NEW.usuario_destino_id, asignado_a_usuario_id),
      estado = 'ACTIVO',
      version = version + 1,
      actualizado_en = NOW()
    WHERE id = NEW.activo_id;

    INSERT INTO movimientos_activos (
      activo_id,
      tipo_movimiento,
      ubicacion_desde_id,
      ubicacion_hasta_id,
      usuario_desde_id,
      usuario_hasta_id,
      estado_desde,
      estado_hasta,
      realizado_por,
      traslado_id,
      notas,
      creado_en
    )
    VALUES (
      NEW.activo_id,
      'TRASLADO',
      NEW.ubicacion_origen_id,
      NEW.ubicacion_destino_id,
      NEW.usuario_origen_id,
      NEW.usuario_destino_id,
      'EN_TRASLADO',
      'ACTIVO',
      COALESCE(NEW.confirmado_por, NEW.aprobado_por, NEW.solicitado_por),
      NEW.id,
      COALESCE(NEW.motivo, 'Traslado completado de forma automatica'),
      NOW()
    );
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_departamentos_actualizado_en ON departamentos;
CREATE TRIGGER trg_departamentos_actualizado_en
BEFORE UPDATE ON departamentos
FOR EACH ROW EXECUTE FUNCTION fn_establecer_actualizado_en();

DROP TRIGGER IF EXISTS trg_usuarios_actualizado_en ON usuarios;
CREATE TRIGGER trg_usuarios_actualizado_en
BEFORE UPDATE ON usuarios
FOR EACH ROW EXECUTE FUNCTION fn_establecer_actualizado_en();

DROP TRIGGER IF EXISTS trg_ubicaciones_actualizado_en ON ubicaciones;
CREATE TRIGGER trg_ubicaciones_actualizado_en
BEFORE UPDATE ON ubicaciones
FOR EACH ROW EXECUTE FUNCTION fn_establecer_actualizado_en();

DROP TRIGGER IF EXISTS trg_categorias_activos_actualizado_en ON categorias_activos;
CREATE TRIGGER trg_categorias_activos_actualizado_en
BEFORE UPDATE ON categorias_activos
FOR EACH ROW EXECUTE FUNCTION fn_establecer_actualizado_en();

DROP TRIGGER IF EXISTS trg_activos_actualizado_en ON activos;
CREATE TRIGGER trg_activos_actualizado_en
BEFORE UPDATE ON activos
FOR EACH ROW EXECUTE FUNCTION fn_establecer_actualizado_en();

DROP TRIGGER IF EXISTS trg_traslados_actualizado_en ON traslados;
CREATE TRIGGER trg_traslados_actualizado_en
BEFORE UPDATE ON traslados
FOR EACH ROW EXECUTE FUNCTION fn_establecer_actualizado_en();

DROP TRIGGER IF EXISTS trg_planes_mantenimiento_actualizado_en ON planes_mantenimiento;
CREATE TRIGGER trg_planes_mantenimiento_actualizado_en
BEFORE UPDATE ON planes_mantenimiento
FOR EACH ROW EXECUTE FUNCTION fn_establecer_actualizado_en();

DROP TRIGGER IF EXISTS trg_movimientos_activos_no_update ON movimientos_activos;
CREATE TRIGGER trg_movimientos_activos_no_update
BEFORE UPDATE ON movimientos_activos
FOR EACH ROW EXECUTE FUNCTION fn_bloquear_cambio_inmutable();

DROP TRIGGER IF EXISTS trg_movimientos_activos_no_delete ON movimientos_activos;
CREATE TRIGGER trg_movimientos_activos_no_delete
BEFORE DELETE ON movimientos_activos
FOR EACH ROW EXECUTE FUNCTION fn_bloquear_cambio_inmutable();

DROP TRIGGER IF EXISTS trg_traslados_completar_aplicar_activo ON traslados;
CREATE TRIGGER trg_traslados_completar_aplicar_activo
AFTER UPDATE ON traslados
FOR EACH ROW EXECUTE FUNCTION fn_completar_traslado_aplicar_activo();

-- =========================
-- INDICES
-- =========================
CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON usuarios(rol);
CREATE INDEX IF NOT EXISTS idx_usuarios_departamento ON usuarios(departamento_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(esta_activo);

CREATE INDEX IF NOT EXISTS idx_ubicaciones_padre ON ubicaciones(padre_id);

CREATE INDEX IF NOT EXISTS idx_activos_codigo ON activos(codigo);
CREATE INDEX IF NOT EXISTS idx_activos_ubicacion ON activos(ubicacion_actual_id);
CREATE INDEX IF NOT EXISTS idx_activos_estado ON activos(estado);
CREATE INDEX IF NOT EXISTS idx_activos_categoria ON activos(categoria_id);
CREATE INDEX IF NOT EXISTS idx_activos_asignado_a ON activos(asignado_a_usuario_id);
CREATE INDEX IF NOT EXISTS idx_activos_no_eliminados ON activos(id) WHERE eliminado_en IS NULL;
CREATE INDEX IF NOT EXISTS idx_activos_etiqueta_rfid ON activos(etiqueta_rfid);

CREATE INDEX IF NOT EXISTS idx_traslados_activo ON traslados(activo_id);
CREATE INDEX IF NOT EXISTS idx_traslados_estado ON traslados(estado);
CREATE INDEX IF NOT EXISTS idx_traslados_creado_en ON traslados(creado_en DESC);
CREATE INDEX IF NOT EXISTS idx_traslados_destino ON traslados(ubicacion_destino_id);

CREATE INDEX IF NOT EXISTS idx_movimientos_activos_activo ON movimientos_activos(activo_id);
CREATE INDEX IF NOT EXISTS idx_movimientos_activos_creado ON movimientos_activos(creado_en DESC);
CREATE INDEX IF NOT EXISTS idx_movimientos_activos_traslado ON movimientos_activos(traslado_id);

CREATE INDEX IF NOT EXISTS idx_sesiones_inventario_ubicacion ON sesiones_inventario(ubicacion_id);
CREATE INDEX IF NOT EXISTS idx_sesiones_inventario_estado ON sesiones_inventario(estado);

CREATE INDEX IF NOT EXISTS idx_items_inventario_sesion ON items_inventario(sesion_id);
CREATE INDEX IF NOT EXISTS idx_items_inventario_activo ON items_inventario(activo_id);
CREATE INDEX IF NOT EXISTS idx_items_inventario_escaneado_en ON items_inventario(escaneado_en DESC);
CREATE UNIQUE INDEX IF NOT EXISTS uq_items_inventario_sesion_activo
  ON items_inventario(sesion_id, activo_id)
  WHERE activo_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_items_inventario_id_evento_cliente
  ON items_inventario(sesion_id, id_evento_cliente)
  WHERE id_evento_cliente IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_cola_sincronizacion_estado ON cola_sincronizacion(estado, creado_en);
CREATE INDEX IF NOT EXISTS idx_cola_sincronizacion_dispositivo ON cola_sincronizacion(dispositivo_id, creado_en);

CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario_no_leido ON notificaciones(usuario_id, esta_leido, creado_en DESC);
CREATE INDEX IF NOT EXISTS idx_sesiones_autenticacion_usuario_expira ON sesiones_autenticacion(usuario_id, expira_en);

CREATE INDEX IF NOT EXISTS idx_ordenes_mantenimiento_activo ON ordenes_mantenimiento(activo_id, estado);
CREATE INDEX IF NOT EXISTS idx_predicciones_ia_activo_creado ON predicciones_ia(activo_id, creado_en DESC);

COMMIT;
