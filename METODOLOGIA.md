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

Fuente oficial: `https://www.datos.gov.co/resource/p6dx-8zbt.json` (dataset SECOP II – Procesos de Contratación, actualización diaria). Se consultaron por separado 24 términos en `nombre_del_procedimiento`, con `estado_de_apertura_del_proceso='Abierto'`, `estado_del_procedimiento='Publicado'` y `adjudicado='No'`.

La consulta produjo 1.387 registros brutos. La selección exigió relación explícita, actualización desde el 1 de noviembre de 2026 y fase de presentación de ofertas; se excluyó contratación directa. Resultado: 27 candidatos. Se conservaron mínima cuantía y régimen especial cuando son mecanismos reales de participación, señalando su modalidad. No se suman presupuestos.

**Limitación crítica:** el dataset no ofrece fecha/hora de cierre. La ficha pública puede solicitar captcha. Los estados abiertos pueden persistir en procesos antiguos; por eso se filtró actualización reciente y se etiqueta cada registro como “confirmar plazo”.

## Evidencia documental

Se descargaron y extrajeron las bases CAF LIF 2026 (17 páginas), términos OCAD Paz 2–4 (23 páginas) y guía OCAD Paz 3 (17 páginas). El Acuerdo 18/Anexo 15 del SGR es un documento escaneado sin capa de texto útil: solo se reporta la vigencia indicada oficialmente y se remite al PDF visual.

## Controles de calidad

- Campos obligatorios y URLs por los 66 registros.
- IDs únicos y referencias locales existentes.
- Pruebas de presets, búsqueda, persistencia URL, detalles, tema, móvil y descarga CSV.
- PDF A4, 87 páginas, sin páginas en blanco, 27 IDs SECOP, 39 títulos base y 84 fuentes esperadas con anotaciones URI.
- Render visual de portada, resumen, página intermedia y cierre.

## Actualización

Edite `research/datos_base.py`, actualice y depure SECOP con los scripts, ejecute los generadores y repita las validaciones. No cambie solo el HTML: PDF, sitio y CSV deben proceder de la misma base. Reconfirme todas las fechas con zona horaria, adendas y disponibilidad presupuestal.
