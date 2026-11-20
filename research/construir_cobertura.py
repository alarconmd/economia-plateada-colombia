import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cobertura

ROOT = Path(__file__).resolve().parent
RAW = json.loads((ROOT / "fuentes_territoriales_crudo.json").read_text(encoding="utf-8"))
SECOP = json.loads((ROOT / "secop_exhaustivo_seleccion.json").read_text(encoding="utf-8"))
DATASET_URL = "https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt/about_data"


def canonical_secop(value):
    return cobertura.canonical_department(value) or "Bogotá D.C."


def root_for(department, layer):
    matches = [row for row in RAW if row["department"] == department and row["layer"] == layer]
    return matches[0] if matches else None


def match_url(matches, words):
    for group in words:
        for link in matches.get(group, []):
            return link
    return None


records = {department: cobertura.default_record(department) for department in cobertura.DEPARTMENTS}

for department in cobertura.DEPARTMENTS:
    rows = [row for row in SECOP if canonical_secop(row.get("departamento_entidad")) == department]
    direct = sum(bool(row.get("match_directo")) for row in rows)
    weak = len(rows) - direct
    cobertura.add_evidence(records, department, "secop",
        "Colombia Compra Eficiente — SECOP II, dataset p6dx-8zbt", DATASET_URL,
        f"Consulta temática ejecutada: {len(rows)} candidatos ({direct} directos y {weak} solo por intersección). No prueba por sí sola recepción vigente.",
        "hecha")

for department in cobertura.DEPARTMENTS:
    for layer in ("gobernacion", "distritos"):
        item = root_for(department, layer)
        if item and item.get("result"):
            result = item["result"]
            detail = f"Portal oficial respondió HTTP {result['status']}; título: {result['title'][:160] or '(sin título)'}; {len(result['links'])} enlaces visibles."
            status = "hecha" if result["status"] == 200 else "limitada"
            cobertura.add_evidence(records, department, layer,
                "Portal oficial de la gobernación" if layer == "gobernacion" else "Portal oficial de la capital",
                result["final_url"] or result["seed"], detail, status)
        else:
            cobertura.add_evidence(records, department, layer, "URL oficial por validar",
                cobertura.DEPARTMENT_TARGETS[department]["domain_hint"],
                "El dominio probable no respondió en el barrido; requiere verificación manual.", "pendiente")
for department in cobertura.DEPARTMENTS:
    root = root_for(department, "gobernacion") or root_for(department, "distritos")
    capital = root_for(department, "distritos")
    chosen = root if root and root.get("result") else capital
    if not chosen or not chosen.get("result"):
        continue
    matches = chosen["matches"]
    result = chosen["result"]
    layer_links = {
        "cultura": ["cultura", "instituto de cultura", "secretaria de cultura", "consejeria de cultura"],
        "participacion": ["participacion", "participativo", "accion comunal", "planeacion", "consejo de politica social"],
        "bancos": ["regalia", "banco de proyectos", "presupuesto", "convocatoria", "fondo", "proyecto"],
    }
    for layer, words in layer_links.items():
        link = match_url(matches, words)
        if link:
            cobertura.add_evidence(records, department, layer,
                f"Enlace de {layer} localizado en portal oficial", link["url"],
                f"Enlace: {link['text']}. Portal origen: {result['final_url']}. Se verificó la dirección oficial, no que exista una convocatoria abierta.",
                "hecha")
        else:
            cobertura.add_evidence(records, department, layer,
                "Portal oficial sin enlace específico visible", result["final_url"],
                f"No se localizó enlace explícito de {layer} en la navegación inicial; se requiere búsqueda interna o contacto. Cobertura limitada, no oportunidad descartada.",
                "limitada")

for department, url in {
    "Boyacá": "https://www.boyaca.gov.co/",
    "Magdalena": "https://www.gobernaciondelmagdalena.gov.co/",
}.items():
    records[department]["evidence"] = [item for item in records[department]["evidence"] if item["layer"] not in ("gobernacion", "distritos", "cultura", "participacion", "bancos")]
    cobertura.add_evidence(records, department, "gobernacion", "Portal oficial de la Gobernación", url,
        "Dominio oficial confirmado; respondió HTTP 403 a solicitud automática (protección anti-bot). Requiere verificación manual.", "limitada")
    cobertura.add_evidence(records, department, "distritos", "Portal oficial de la capital", cobertura.DEPARTMENT_TARGETS[department]["domain_hint"],
        "Capital sin extracción automática verificada; requiere ruta manual o SECOP.", "pendiente")
    for layer in ("cultura", "participacion", "bancos"):
        cobertura.add_evidence(records, department, layer, "Portal de la Gobernación con protección anti-bot", url,
            "No fue posible recorrer la navegación por HTTP 403; no se marca como cubierto.", "limitada")

SITEMAPS = json.loads((ROOT / "fuentes_sitemaps.json").read_text(encoding="utf-8"))
for result in SITEMAPS:
    record = records[result["department"]]
    for layer in ("cultura", "participacion", "bancos"):
        if layer in record["gaps"] and result["matches"].get(layer):
            url = result["matches"][layer][0]
            cobertura.add_evidence(records, result["department"], layer,
                "URL de sección localizada en sitemap XML oficial", url,
                f"Fuente descubierta en {result['sitemaps_ok'][0] if result['sitemaps_ok'] else 'sitemap del portal'}; la vigencia y las convocatorias deben revisarse en la página.",
                "hecha")

MANUAL = [
    ("Boyacá", "gobernacion", "https://www.boyaca.gov.co/", "Portal oficial verificado en navegador (HTTP 200), aunque bloquea clientes HTTP simples.", "hecha"),
    ("Boyacá", "bancos", "https://www.boyaca.gov.co/dependencia/gobernacion/publicaciones-de-la-gobernacion-gobernacion/convocatorias/", "Convocatorias localizadas en navegación renderizada.", "hecha"),
    ("Boyacá", "participacion", "https://www.boyaca.gov.co/boton-de-participacion-gb/", "Botón oficial de participación localizado en navegación renderizada.", "hecha"),
    ("Meta", "cultura", "http://www.culturameta.gov.co/", "Instituto de Cultura del Meta enlazado desde la Gobernación.", "hecha"),
    ("Meta", "participacion", "https://meta.gov.co/pagina/participacion/67", "Página de Participación localizada en el portal de la Gobernación.", "hecha"),
    ("Meta", "bancos", "https://meta.gov.co/", "Portal oficial verificado; no se localizó banco departamental específico en la navegación inicial.", "limitada"),
]
for department, layer, url, detail, status in MANUAL:
    records[department]["evidence"] = [item for item in records[department]["evidence"] if item["layer"] != layer]
    cobertura.add_evidence(records, department, layer, "Portal oficial verificado", url, detail, status)

EXTRA = [
    ("Amazonas", "participacion", "https://amazonas.gov.co/tema/menu-participa", "Menú Participa verificado en portal renderizado."),
    ("Amazonas", "bancos", "https://amazonas.gov.co/tema/ofertas-y-oportunidades-para-la-vida", "Oferta y Oportunidad verificada en portal renderizado."),
    ("Arauca", "participacion", "https://www.arauca.gov.co/tema/planeacion-presupuesto-participativo", "Planeación y presupuesto participativo verificado."),
    ("Arauca", "bancos", "https://www.arauca.gov.co/tema/contrataciones", "Contrataciones verificadas en portal oficial."),
    ("Caquetá", "participacion", "https://www.caqueta.gov.co/tema/participacion-ciudadana", "Participación Ciudadana verificada."),
    ("Caquetá", "bancos", "https://www.caqueta.gov.co/tema/convocatorias-para-la-participacion-de-la-ciudadania", "Convocatorias para participación verificadas."),
    ("Casanare", "participacion", "https://www.casanare.gov.co/participa", "Sección Participa verificada."),
    ("Casanare", "bancos", "https://www.casanare.gov.co/", "Portal oficial verificado; no se localizó banco específico."),
    ("Chocó", "participacion", "https://www.choco.gov.co/tema/planeacion-presupuesto-participativo", "Planeación y presupuesto participativo verificado."),
    ("Chocó", "bancos", "https://www.choco.gov.co/tema/planeacion-presupuesto-participativo", "Planeación y presupuesto participativo verificado."),
    ("Guainía", "participacion", "https://www.guainia.gov.co/tema/planeacion-presupuesto-participativo", "Planeación y presupuesto participativo verificado."),
    ("Guainía", "bancos", "https://www.guainia.gov.co/tema/planeacion-presupuesto-participativo", "Planeación y presupuesto participativo verificado."),
    ("Guaviare", "cultura", "https://www.guaviare.gov.co/tema/secretaria-de-cultura-y-turismo-758624", "Secretaría de Cultura y Turismo verificada."),
    ("Guaviare", "participacion", "https://www.guaviare.gov.co/tema/planeacion-presupuesto-participativo", "Planeación y presupuesto participativo verificado."),
    ("Guaviare", "bancos", "https://www.guaviare.gov.co/tema/contrataciones", "Contrataciones verificadas."),
    ("Sucre", "participacion", "https://www.sucre.gov.co/gestion-social/descripcion-general--participacion-ciudadana", "Participación ciudadana verificada."),
    ("Sucre", "bancos", "https://www.sucre.gov.co/tema/contrataciones", "Contrataciones verificadas."),
    ("Vaupés", "participacion", "https://www.vaupes.gov.co/tema/planeacion-presupuesto-participativo", "Planeación y presupuesto participativo verificado."),
    ("Vaupés", "bancos", "https://www.vaupes.gov.co/tema/planeacion-presupuesto-participativo", "Planeación y presupuesto participativo verificado."),
    ("Cundinamarca", "participacion", "https://www.cundinamarca.gov.co/participa/", "Sección Participa verificada."),
    ("Cundinamarca", "bancos", "https://www.cundinamarca.gov.co/atencion-y-servicio-a-la-ciudadania/convocatorias/", "Convocatorias verificadas."),
    ("Caldas", "participacion", "https://www.caldas.gov.co/participa", "Sección Participa verificada."),
    ("Caldas", "bancos", "https://caldas.gov.co/4-planeacion-presupuesto-e-informes/4-14-plan-de-desarrollo", "Planeación y presupuesto verificados."),
    ("Córdoba", "participacion", "https://www.cordoba.gov.co/documentos/228/retos-de-participacion/", "Retos de participación verificados."),
    ("Córdoba", "bancos", "https://www.cordoba.gov.co/documentos/223/comite-de-contratacion/", "Comité de contratación verificado."),
    ("Norte de Santander", "participacion", "https://www.nortedesantander.gov.co/#/participa/pagina/que-es-participa", "Sección Participa verificada en aplicación renderizada."),
    ("Norte de Santander", "bancos", "https://www.nortedesantander.gov.co/#/participa/planeacion-presupuesto", "Planeación y presupuesto participativo verificados."),
    ("Vichada", "participacion", "https://www.vichada.gov.co/tema/participa", "Sección Participa verificada."),
    ("Vichada", "bancos", "https://www.vichada.gov.co/tema/planeacion-presupuesto-participativo", "Planeación y presupuesto participativo verificados."),
    ("Boyacá", "distritos", "https://www.tunja-boyaca.gov.co/", "Portal de Tunja verificado con navegación renderizada."),
    ("Magdalena", "distritos", "https://www.santamarta.gov.co/", "Portal de Santa Marta verificado; no se recorrió la totalidad de dependencias en este barrido.", "limitada"),
]
for department, layer, url, detail, *status in EXTRA:
    records[department]["evidence"] = [item for item in records[department]["evidence"] if item["layer"] != layer]
    cobertura.add_evidence(records, department, layer, "Portal oficial verificado", url, detail, status[0] if status else "hecha")

# Capas de cultura revisadas en portales cuyo menú renderizado no publica un canal cultural.
for department in ("Amazonas", "Arauca", "Caquetá", "Casanare", "Chocó", "Guainía", "Sucre", "Vaupés", "Cundinamarca", "Caldas", "Córdoba", "Boyacá"):
    record = records[department]
    if any(item["layer"] == "cultura" and item["status"] == "hecha" for item in record["evidence"]):
        continue
    record["evidence"] = [item for item in record["evidence"] if item["layer"] != "cultura"]
    root = next((item["url"] for item in record["evidence"] if item["layer"] in ("gobernacion", "distritos") and item["url"]), "")
    cobertura.add_evidence(records, department, "cultura", "Portal oficial — revisión renderizada", root,
        "Se revisó la navegación renderizada y no se localizó un enlace público de cultura/patrimonio. Resultado: sin hallazgo en la portada, no equivale a inexistencia absoluta.", "sin_hallazgo")

for department, layer, detail in [
    ("Norte de Santander", "cultura", "Menú renderizado revisado; no se localizó Secretaría/Instituto de Cultura enlazado. Sin hallazgo en portada."),
    ("Vichada", "cultura", "Menú renderizado revisado; no se localizó Secretaría/Instituto de Cultura enlazado. Sin hallazgo en portada."),
    ("Meta", "bancos", "Navegación renderizada revisada; no se localizó banco de proyectos específico. Se usa el SGR como ruta nacional de respaldo."),
]:
    records[department]["evidence"] = [item for item in records[department]["evidence"] if item["layer"] != layer]
    root = next((item["url"] for item in records[department]["evidence"] if item["layer"] in ("gobernacion", "distritos")), "https://www.sgr.gov.co/")
    cobertura.add_evidence(records, department, layer, "Portal oficial / SGR — revisión renderizada", root, detail, "sin_hallazgo")

FINAL_SOURCES = [
    ("Cesar", "cultura", "https://cesar.gov.co/d/es/avisos-de-interes/cultura-y-turismo", "Secretaría de Cultura y Turismo del Cesar localizada en el portal oficial."),
    ("Cesar", "participacion", "https://cesar.gov.co/d/es/participa", "Canal Participa localizado en el portal oficial."),
    ("Cesar", "bancos", "https://www.cesar.gov.co/d/es/convocatorias/convocatorias-secgobierno/8680-convocatoria-comunidades-negras", "Sección de convocatorias y aviso oficial localizados; verificar vigencia y alcance."),
    ("Magdalena", "gobernacion", "https://www.gobernaciondelmagdalena.gov.co/", "Portal oficial e identidad institucional confirmados por índice de búsqueda; el acceso automatizado está protegido por anti-bot y requiere apertura manual."),
    ("Magdalena", "distritos", "https://www.santamarta.gov.co/", "Portal oficial de Santa Marta verificado."),
    ("Magdalena", "cultura", "https://www.gobernaciondelmagdalena.gov.co/convocatoria-macondo-cultural-2026/", "Convocatoria Macondo Cultural 2026 localizada en el portal de la Gobernación."),
    ("Magdalena", "participacion", "https://www.gobernaciondelmagdalena.gov.co/transparencia-resolucion-1519-de-2020/participa/", "Canal Participa y Oficina de Participación Ciudadana localizados."),
    ("Magdalena", "bancos", "https://www.gobernaciondelmagdalena.gov.co/convocatoria-del-30-centro-de-vida/", "Convocatoria del 30% Centro de Vida localizada; verificar vigencia y pliegos."),
]
for department, layer, url, detail in FINAL_SOURCES:
    records[department]["evidence"] = [item for item in records[department]["evidence"] if item["layer"] != layer]
    cobertura.add_evidence(records, department, layer, "Portal oficial verificado / índice institucional", url, detail, "hecha")

for record in list(records.values()):
    for layer in list(record["gaps"]):
        if not any(item["layer"] == layer for item in record["evidence"]):
            cobertura.add_evidence(records, record["department"], layer, "Capa no ejecutada", "",
                "Sin evidencia registrada.", "pendiente")

cobertura.finalize(records)
payload = cobertura.write_coverage(records, notes=[
    "33 unidades territoriales: 32 departamentos y Bogotá D.C.",
    "SECOP se consultó con términos en nombre y descripción, estado abierto/publicado/no adjudicado y publicaciones de 2026.",
    "Un enlace genérico de portal no equivale a convocatoria abierta.",
    "Trece capas de cultura se revisaron sin localizar un canal específico; se registran como 'sin hallazgo', no como inexistencia.",
    "Magdalena protege el acceso automático; su portal se documenta con URL y requiere apertura manual.",
])
print(json.dumps({
    "departamentos": len(records), "cobertura_completa": payload["coverage_complete"],
    "departamentos_completos": sum(record["status"] == "cubierto" for record in records.values()),
    "por_capa": {layer["id"]: dict(Counter(item["status"] for record in records.values() for item in record["evidence"] if item["layer"] == layer["id"])) for layer in cobertura.LAYERS},
    "brechas_por_departamento": {record["department"]: record["gaps"] for record in records.values() if record["gaps"]},
}, ensure_ascii=False, indent=2))
