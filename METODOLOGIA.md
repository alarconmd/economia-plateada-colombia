# Metodología y actualización

## Definición operativa

Economía plateada incluye soluciones para o lideradas por personas mayores; envejecimiento activo/saludable; salud y geriatría; cuidado y dependencia; emprendimiento/empleo senior; inclusión financiera/digital; tecnología de asistencia; accesibilidad, vivienda, movilidad, cultura, recreación y participación. La edad concreta (50+, 60+) depende de cada fuente.

## Estados

- `abierta`: canal actual o recepción permanente confirmada en la fuente.
- `activa`: programa, servicio, norma o proyecto vigente, sin asumir postulación abierta.
- `proxima`: fecha futura estimada, sin bases finales.
- `historico`: antecedente o ruta sin ventana específica verificada.
- `cerrada`: plazo superado, adjudicada o resultados publicados.
- `pausada`: fuente suspendida por el financiador.
- `no_elegible`: sede/geografía o prioridad excluye una solicitud directa desde Colombia.
- `secop`: registro candidato del dataset; cierre y recepción deben verificarse en el aviso.

## SECOP II

Fuente oficial: `https://www.datos.gov.co/resource/p6dx-8zbt.json` (actualización diaria). Universo de trabajo: procesos abiertos, publicados, no adjudicados y con publicación desde 2026. Se consultaron 34 términos en **nombre y descripción** con 68 consultas independientes.

La consulta produjo **12.850 registros candidatos**. El embudo operativo exige fase de oferta/manifestación, exclusión de contratación directa y actualización desde el 1 de octubre de 2026. Quedaron **952 candidatos**: 351 coincidencias directas y 601 intersecciones (cuidado, discapacidad o 60 años) que requieren validación del objeto. Los municipios abiertos entran por esta vía, no por una enumeración manual.

**Limitación crítica:** el dataset no ofrece fecha/hora de cierre y la ficha pública puede pedir captcha. “Publicado” y “abierto” no prueba recepción vigente. Todo candidato debe abrirse y contrastarse con el pliego.

## Cobertura territorial

Se auditaron 33 unidades: 32 departamentos y Bogotá D.C. Para cada una se revisan seis capas: SECOP II; gobernación; capital/distrito; cultura; participación/planeación; y bancos/regalías/fondos. Las fuentes se buscan en portales oficiales, navegación HTML, renderizado JavaScript y sitemaps XML.

Estados: **Hallazgo** (URL localizada), **Sin hallazgo** (navegación revisada sin canal visible), **Limitada** (bloqueo o menú no disponible) y **Pendiente** (capa no ejecutada). Al corte: **31/33 territorios con seis capas resueltas**; Cesar y Magdalena tienen brechas explícitas. La matriz no interpreta ausencia de enlace como ausencia de oportunidad.

## Evidencia documental

Se descargaron y extrajeron las bases CAF LIF 2026 (17 páginas), términos OCAD Paz 2–4 (23 páginas) y guía OCAD Paz 3 (17 páginas). El Acuerdo 18/Anexo 15 del SGR es un documento escaneado sin capa de texto útil: solo se reporta la vigencia indicada oficialmente y se remite al PDF visual.

## Controles de calidad

- Campos obligatorios y URLs por los 991 registros.
- IDs únicos, referencias locales existentes y 33 territorios en la matriz.
- Pruebas de presets, búsqueda, persistencia URL, paginación, señal directa/intersección, detalles, tema, móvil, CSV y cobertura.
- PDF A4 de 151 páginas, sin páginas en blanco, 952 IDs SECOP, 39 fichas fuente, 33 territorios y 1.150 enlaces únicos.
- Render visual de portada, resumen, tabla SECOP y cierre.

## Actualización

Edite `research/datos_base.py`, actualice y depure SECOP con `consultar_secop_exhaustivo.py`/`seleccionar_secop.py`, reconstruya fuentes y cobertura, ejecute los generadores y repita las validaciones. No cambie solo el HTML: PDF, sitio y CSV deben proceder de la misma base. Reconfirme fechas con zona horaria, adendas y disponibilidad presupuestal.
