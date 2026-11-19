# Economía Plateada Colombia

Informe y explorador estático sobre iniciativas y financiación para proyectos de economía plateada en Bogotá–Cundinamarca, el resto de Colombia, SECOP II, regalías, ministerios, ONG y cooperación internacional.

## Entregables en línea

- Explorador: https://alarconmd.github.io/economia-plateada-colombia/
- Informe HTML: https://alarconmd.github.io/economia-plateada-colombia/documento.html
- PDF: https://alarconmd.github.io/economia-plateada-colombia/Informe_Economia_Plateada_Colombia_19NOV2026.pdf
- Dataset resumen: https://alarconmd.github.io/economia-plateada-colombia/oportunidades.csv

## Alcance y corte

- Corte general y SECOP: **19 de noviembre de 2026**; SECOP a las **09:32, hora de Colombia**.
- 66 registros: 39 iniciativas/fuentes y 27 candidatos SECOP II.
- El informe distingue subvenciones, contratación, inversión pública, asistencia técnica, aceleración, beneficios individuales, kits y crowdfunding.
- Un registro SECOP marcado como “publicado/abierto/no adjudicado” **no garantiza recepción vigente**. El dataset `p6dx-8zbt` no expone la fecha/hora de cierre; hay que abrir el aviso y revisar los documentos.
- No es una revisión exhaustiva de todas las gobernaciones y municipios ni asesoría jurídica. Consulte `documento.html#metodo`.

## Uso local

No requiere compilación ni dependencias para visualizar:

```bash
python -m http.server 8765
```

Abrir `http://127.0.0.1:8765/`. El `index.html` contiene HTML, CSS, JavaScript y datos en un solo archivo.

## Funcionalidades

Búsqueda, filtros por capítulo/estado/postulante/tema/presencia, cinco presets, orden, detalles expandibles, enlaces compartibles, exportación CSV, impresión, briefing copiable y tema claro/oscuro. No usa analítica, cookies de seguimiento ni recursos externos de JavaScript/CSS.

## Reproducir los entregables

Con Python y `requests` instalados:

```bash
python research/datos_base.py
python research/preparar_datos.py
python research/generar_documento.py
python research/generar_sitio.py
python research/validar_entregables.py
```

`consultar_secop.py`, `seleccionar_secop.py` y `descargar_pdfs.py` documentan la actualización de insumos. Al actualizar SECOP deben depurarse manualmente los objetos y fechas; no basta ejecutar la consulta.

## Estructura

- `index.html`: explorador autocontenido.
- `documento.html` + `informe.css`: informe editorial con enlaces.
- `Informe_Economia_Plateada_Colombia_19NOV2026.pdf`: informe de 87 páginas A4.
- `oportunidades.csv`: resumen de los 66 registros.
- `research/`: base, consultas, generadores y validación.

Fuente SECOP: Agencia Nacional de Contratación Pública–Colombia Compra Eficiente, dataset **SECOP II – Procesos de Contratación**, `p6dx-8zbt`, licencia indicada en datos.gov.co. Las demás fuentes y URLs están citadas en cada ficha.
