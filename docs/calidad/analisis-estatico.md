# Análisis estático — triaje de hallazgos

Este documento registra qué hace el equipo con lo que reporta el análisis estático de
seguridad (SonarQube / SonarCloud) sobre el código de UniTeam.

**Un hallazgo no es un defecto.** La herramienta reconoce patrones, no intenciones: no sabe si
una contraseña es la de producción o la de un contenedor que se borra al terminar, ni si una URL
la escribe un atacante o quien ejecuta el script. Por eso cada hallazgo se cierra de una de tres
maneras, y **ninguna de ellas es ignorarlo en silencio**:

| Veredicto | Qué significa |
|-----------|---------------|
| **Corregido** | El hallazgo señalaba algo real. Se cambió el código. |
| **Aceptado** | El riesgo existe pero es proporcionado al contexto, y se deja constancia de por qué. |
| **Falso positivo** | El patrón coincide, pero la condición que lo haría explotable no se da. |

---

## Hallazgos y veredictos

### 1. Campos opcionales de Pydantic sin valor por defecto — **corregido**

**Dónde:** [`app/api/esquemas.py`](../../app/api/esquemas.py), `TareaSalida.responsable` y
`TareaSalida.fecha_limite`.

En Pydantic v2, `Optional[str]` **sin** `= None` declara un campo *obligatorio que admite
nulo*: hay que pasarlo siempre, aunque sea como `None`. Es justo lo contrario de lo que el
nombre sugiere, y de lo que el resto del esquema hace: `CrearTarea` sí llevaba `= None`. La
incoherencia no se notaba porque ambos campos se rellenan siempre desde el dominio, pero
convertía en obligatorio algo que el modelo de dominio considera opcional.

Se añadió `= None` a los dos campos.

### 2. `npm install` en lugar de `npm ci`, y sin `--ignore-scripts` — **corregido**

**Dónde:** [`web/Dockerfile`](../../web/Dockerfile) y el trabajo `frontend` de
[`ci.yml`](../../.github/workflows/ci.yml).

`npm install` puede **actualizar** `package-lock.json` durante la instalación: una compilación
reproducible deja de serlo, y el cierre de versiones que el repositorio guarda deja de describir
lo que realmente se instaló. `npm ci` instala exactamente lo que fija el cierre y falla si el
manifiesto y el cierre no concuerdan.

`--ignore-scripts` impide que las dependencias ejecuten sus *scripts* de instalación
(`preinstall`, `postinstall`) al construir la imagen. Es la vía por la que un paquete
comprometido ejecuta código en la máquina que compila, sin que nadie lo importe nunca.

Ambos comandos son ahora `npm ci --ignore-scripts`. Se retiró también el respaldo
`|| npm install` del `Dockerfile`, que anulaba la garantía: si `npm ci` fallaba por un cierre
desactualizado, el respaldo lo tapaba.

### 3. `pip install` sin cierre de versiones ni verificación de huella — **corregido**

**Dónde:** [`Dockerfile`](../../Dockerfile) y el trabajo `pruebas` de
[`ci.yml`](../../.github/workflows/ci.yml).

El frontend tenía cierre de versiones (`package-lock.json`) y el backend no: `requirements.txt`
fija las dependencias **directas** y deja las transitivas a lo que PyPI sirva ese día. Dos
compilaciones de la misma revisión podían instalar árboles distintos.

Se añadió [`requirements.lock.txt`](../../requirements.lock.txt), generado con
`pip-compile --generate-hashes`, que fija las 33 dependencias del árbol completo con la huella
SHA-256 de cada rueda aceptable. La imagen y la integración continua instalan de ahí, con dos
banderas:

- `--require-hashes`: pip rechaza cualquier archivo cuya huella no coincida.
- `--only-binary :all:`: se instalan solo ruedas ya compiladas. Sin esta bandera, pip puede
  descargar un *sdist* y **ejecutar su `setup.py`** para construirlo, que es por donde un
  paquete comprometido consigue ejecución de código durante la instalación.

`requirements.txt` sigue siendo la lista legible de dependencias directas —lo que el proyecto
necesita— y `requirements.lock.txt` es lo que realmente se instala, igual que la pareja
`package.json` / `package-lock.json` del frontend. El trabajo `cierre` de la integración
continua recompila el cierre en cada `push` y falla si no coincide con el del repositorio, para
que no puedan separarse.

### 4. Petición a una URL construida desde configuración externa (SSRF) — **corregido parcialmente**

**Dónde:** [`app/api/seguridad.py`](../../app/api/seguridad.py), `_descubrir_jwks`.

La API descarga el documento de descubrimiento del emisor OIDC desde una URL que sale de la
variable `OIDC_EMISOR`. La herramienta lo marca como SSRF.

**No es SSRF en sentido estricto:** un SSRF explotable exige que la URL venga de la *petición*,
y aquí viene de la configuración del despliegue, que escribe quien despliega. Ninguna ruta de la
API deja que un usuario influya en ese valor.

Aun así se corrigió lo que sí era una debilidad real: `urllib.request.urlopen` no habla solo
HTTP. Acepta también `file://`, y un `OIDC_EMISOR` mal escrito —o alterado por quien pudiera
tocar el entorno— convertía la búsqueda del JWKS en una lectura del disco de la API. Ahora se
comprueba el esquema antes de abrir la URL, y también el de `OIDC_JWKS_URL`. Lo cubre
`test_un_emisor_que_no_es_http_se_rechaza_al_descubrir_el_jwks` en
[`test/test_autenticacion.py`](../../test/test_autenticacion.py).

Queda como defensa en profundidad, no como control de acceso: el control de acceso de UniTeam
es [ESC-03](escenarios-calidad.md#esc-03).

### 5. URL tomada de los argumentos de línea de órdenes (SSRF) — **falso positivo, con refuerzo**

**Dónde:** [`scripts/medir_esc01.py`](../../scripts/medir_esc01.py) (`--url`) y
[`scripts/token_dev.py`](../../scripts/token_dev.py) (`--emisor`).

Son herramientas de desarrollo que se ejecutan a mano desde una terminal. La URL la escribe la
misma persona que ejecuta el proceso, así que no hay cruce de frontera de confianza: quien
pudiera pasar un `--url` malicioso ya tiene ejecución de órdenes en esa máquina y no necesita el
script. No forman parte de la aplicación desplegada.

Se añadió de todos modos la misma comprobación de esquema que en el punto anterior, porque
cuesta tres líneas y evita que una errata se convierta en una lectura de disco.

### 6. Credenciales de base de datos en el repositorio — **aceptado**

**Dónde:** [`compose.yaml`](../../compose.yaml) y el servicio `mysql` de
[`ci.yml`](../../.github/workflows/ci.yml), con `uniteam` como usuario y contraseña.

El repositorio es público y el contrato del curso prohíbe credenciales en él. Estas no lo
son, y conviene ser preciso sobre por qué:

- No abren nada. Son las de un contenedor MySQL que **se crea y se destruye en la máquina de
  quien desarrolla** o en el corredor efímero de la integración continua, sin puerto expuesto a
  ninguna red que no sea la suya.
- No existe despliegue. UniTeam no tiene entorno de producción
  ([restricción T3](../arc42/arc42-uniteam.md#21-restricciones-técnicas)); cuando lo tenga,
  `DATABASE_URL` vendrá del entorno, que es lo que ya hace la API: `compose.yaml` la inyecta,
  no está incrustada en el código.
- Esconderlas empeoraría la entrega. `docker compose up` como único requisito es una promesa que
  el README hace y que un archivo `.env` que hay que rellenar a mano rompería, sin ganar nada:
  el valor seguiría estando en el historial, solo que en otro archivo.

**Lo que el equipo sí se compromete a sostener:** ninguna credencial de un servicio real
—proveedor OIDC institucional, base de datos desplegada, `SONAR_TOKEN`— entra en el repositorio.
Esas van en los secretos de GitHub Actions o en variables de entorno del despliegue.

Si en algún momento UniTeam se despliega de verdad, este veredicto caduca y hay que revisarlo.

---

## Deuda conocida que el análisis estático no señala

Encontrada al revisar los hallazgos, y anotada aquí para no perderla:

- **La imagen de la API incluye el emisor OIDC de desarrollo** (`scripts/emisor_dev.py`) y las
  dependencias de prueba (`pytest`, `httpx`). El `Dockerfile` copia `scripts/` entero y
  `requirements.txt` no separa lo que hace falta para ejecutar de lo que hace falta para probar.
  No es explotable hoy —el emisor solo arranca si alguien lo invoca—, pero una imagen de
  producción no debería poder firmar tokens sin comprobar contraseñas. Se separará cuando exista
  un despliegue que defender.
- **No hay migraciones de esquema.** Las tablas se crean al arrancar. Sirve para el prototipo;
  no sirve para una base de datos con datos que conservar.

---

## Documentos relacionados

- [Escenarios de calidad](escenarios-calidad.md) · [ESC-03 — control de acceso](escenarios-calidad.md#esc-03)
- [Tabla de aspectos](../aspectos.md)
- [arc42 §2 — Restricciones](../arc42/arc42-uniteam.md#2-restricciones)
- [Registro de uso de IA](../ia.md)
