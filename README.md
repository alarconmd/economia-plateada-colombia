# Economía Plateada Colombia

Informe y explorador estático sobre iniciativas y financiación para proyectos de economía plateada en Bogotá–Cundinamarca, el resto de Colombia, SECOP II, regalías, ministerios, ONG y cooperación internacional.

## Entregables en línea

- Explorador: https://alarconmd.github.io/economia-plateada-colombia/
- Informe HTML: https://alarconmd.github.io/economia-plateada-colombia/documento.html
- PDF: https://alarconmd.github.io/economia-plateada-colombia/Informe_Economia_Plateada_Colombia_19NOV2026.pdf
- Dataset resumen: https://alarconmd.github.io/economia-plateada-colombia/oportunidades.csv

## Alcance y corte

- Corte general y SECOP: **19 de noviembre de 2026**; SECOP a las **18:45, hora de Colombia**.
- **991 registros**: 39 iniciativas/fuentes y 952 candidatos SECOP II.
- **33 territorios auditados**: 32 departamentos y Bogotá D.C.; seis capas por territorio.
- SECOP: 12.850 procesos abiertos/publicados/no adjudicados de 2026 consultados en nombre y descripción; 952 candidatos operativos, **351 directos** y **601 de intersección por validar**.
- Un candidato SECOP **no garantiza recepción vigente**. El dataset `p6dx-8zbt` no expone fecha/hora de cierre; abra el aviso y revise los documentos.
- **31/33** territorios tienen las seis capas resueltas; Cesar y Magdalena mantienen brechas documentadas. “Sin hallazgo” no equivale a inexistencia de financiación.
- No es una revisión uno-a-uno de todos los municipios: los procesos municipales abiertos se cubren vía SECOP II y las rutas departamentales/nacionales. Consulte `documento.html#fuentes`.

## Uso local

No requiere compilación ni dependencias para visualizar:

```bash
python -m http.server 8765
```

Abrir `http://127.0.0.1:8765/`. El `index.html` contiene HTML, CSS, JavaScript y datos en un solo archivo.

## Funcionalidades

Búsqueda, filtros por capítulo/estado/señal SECOP/postulante/tema/presencia, cinco presets, orden, detalles expandibles, paginación de 40, enlaces compartibles, exportación CSV, impresión, briefing copiable y tema claro/oscuro. El tablero `cobertura.html` contiene 33 territorios × 6 capas con evidencia y brechas. No usa analítica, cookies de seguimiento ni recursos externos de JavaScript/CSS.

## Reproducir los entregables

Con Python y `requests` instalados:

```bash
python research/datos_base.py
python research/consultar_secop_exhaustivo.py
python research/seleccionar_secop.py
python research/descubrir_fuentes_territoriales.py
python research/descubrir_sitemaps.py
python research/construir_cobertura.py
python research/preparar_datos.py
python research/generar_documento_v2.py
python research/generar_sitio.py
python research/generar_cobertura.py
python research/validar_entregables_v2.py
```

`consultar_secop_exhaustivo.py` usa la API oficial; `seleccionar_secop.py` aplica el embudo temático. Los portales pueden cambiar y requerir renderizado o revisión manual. No basta ejecutar la consulta para declarar una oportunidad abierta.

## Estructura

- `index.html`: explorador autocontenido de los 991 registros, con paginación.
- `cobertura.html`: tablero interactivo de 33 territorios × 6 capas.
- `documento.html` + `informe.css`: informe editorial con enlaces.
- `Informe_Economia_Plateada_Colombia_19NOV2026.pdf`: informe exhaustivo de 151 páginas A4.
- `oportunidades.csv`: resumen de los 991 registros.
- `secop_oportunidades.csv`: universo SECOP de 952 candidatos.
- `cobertura_territorial.json`: evidencia de las seis capas y brechas.
- `research/`: consultas, base, generadores y validaciones.

Fuente SECOP: Agencia Nacional de Contratación Pública–Colombia Compra Eficiente, dataset **SECOP II – Procesos de Contratación**, `p6dx-8zbt`, licencia indicada en datos.gov.co. Las demás fuentes y URLs están citadas en cada ficha.
