import json
import unicodedata
from pathlib import Path

RESEARCH = Path(__file__).resolve().parent
COBERTURA = RESEARCH / "cobertura_territorial.json"

DEPARTMENTS = [
    "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bogotá D.C.", "Bolívar", "Boyacá",
    "Caldas", "Caquetá", "Casanare", "Cauca", "Cesar", "Chocó", "Córdoba", "Cundinamarca",
    "Guainía", "Guaviare", "Huila", "La Guajira", "Magdalena", "Meta", "Nariño",
    "Norte de Santander", "Putumayo", "Quindío", "Risaralda", "San Andrés y Providencia",
    "Santander", "Sucre", "Tolima", "Valle del Cauca", "Vaupés", "Vichada",
]

# Identificador declarado + reglas operativas para localizar fuentes por departamento.
DEPARTMENT_TARGETS = {
    "Amazonas": {"slug": "amazonas", "domain_hint": "amazonas.gov.co", "seats": ["Leticia"]},
    "Antioquia": {"slug": "antioquia", "domain_hint": "antioquia.gov.co", "seats": ["Medellín", "Medellin"]},
    "Arauca": {"slug": "arauca", "domain_hint": "arauca.gov.co", "seats": ["Arauca"]},
    "Atlántico": {"slug": "atlantico", "domain_hint": "atlantico.gov.co", "seats": ["Barranquilla", "Soledad"]},
    "Bogotá D.C.": {"slug": "bogota", "domain_hint": "bogota.gov.co", "seats": ["Bogotá", "Bogota"], "unified": True},
    "Bolívar": {"slug": "bolivar", "domain_hint": "bolivar.gov.co", "seats": ["Cartagena"]},
    "Boyacá": {"slug": "boyaca", "domain_hint": "boyaca.gov.co", "seats": ["Tunja"]},
    "Caldas": {"slug": "caldas", "domain_hint": "caldas.gov.co", "seats": ["Manizales"]},
    "Caquetá": {"slug": "caqueta", "domain_hint": "caqueta.gov.co", "seats": ["Florencia"]},
    "Casanare": {"slug": "casanare", "domain_hint": "casanare.gov.co", "seats": ["Yopal"]},
    "Cauca": {"slug": "cauca", "domain_hint": "cauca.gov.co", "seats": ["Popayán"]},
    "Cesar": {"slug": "cesar", "domain_hint": "cesar.gov.co", "seats": ["Valledupar"]},
    "Chocó": {"slug": "choco", "domain_hint": "choco.gov.co", "seats": ["Quibdó", "Quibdo"]},
    "Córdoba": {"slug": "cordoba", "domain_hint": "cordoba.gov.co", "seats": ["Montería", "Monteria"]},
    "Cundinamarca": {"slug": "cundinamarca", "domain_hint": "cundinamarca.gov.co", "seats": ["Bogotá", "Bogota"]},
    "Guainía": {"slug": "guainia", "domain_hint": "guainia.gov.co", "seats": ["Inírida", "Inirida"]},
    "Guaviare": {"slug": "guaviare", "domain_hint": "guaviare.gov.co", "seats": ["San José del Guaviare", "San Jose del Guaviare"]},
    "Huila": {"slug": "huila", "domain_hint": "huila.gov.co", "seats": ["Neiva"]},
    "La Guajira": {"slug": "la-guajira", "domain_hint": "laguajira.gov.co", "seats": ["Riohacha"]},
    "Magdalena": {"slug": "magdalena", "domain_hint": "magdalena.gov.co", "seats": ["Santa Marta"]},
    "Meta": {"slug": "meta", "domain_hint": "meta.gov.co", "seats": ["Villavicencio"]},
    "Nariño": {"slug": "narino", "domain_hint": "narino.gov.co", "seats": ["Pasto"]},
    "Norte de Santander": {"slug": "norte-de-santander", "domain_hint": "nortedesantander.gov.co", "seats": ["Cúcuta", "Cucuta"]},
    "Putumayo": {"slug": "putumayo", "domain_hint": "putumayo.gov.co", "seats": ["Mocoa"]},
    "Quindío": {"slug": "quindio", "domain_hint": "quindio.gov.co", "seats": ["Armenia"]},
    "Risaralda": {"slug": "risaralda", "domain_hint": "risaralda.gov.co", "seats": ["Pereira"]},
    "San Andrés y Providencia": {"slug": "san-andres-y-providencia", "domain_hint": "sanandres.gov.co", "seats": ["San Andrés", "San Andres"]},
    "Santander": {"slug": "santander", "domain_hint": "santander.gov.co", "seats": ["Bucaramanga"]},
    "Sucre": {"slug": "sucre", "domain_hint": "sucre.gov.co", "seats": ["Sincelejo"]},
    "Tolima": {"slug": "tolima", "domain_hint": "tolima.gov.co", "seats": ["Ibagué", "Ibague"]},
    "Valle del Cauca": {"slug": "valle-del-cauca", "domain_hint": "valledelcauca.gov.co", "seats": ["Cali"]},
    "Vaupés": {"slug": "vaupes", "domain_hint": "vaupes.gov.co", "seats": ["Mitú", "Mitu"]},
    "Vichada": {"slug": "vichada", "domain_hint": "vichada.gov.co", "seats": ["Puerto Carreño", "Puerto Carreno"]},
}
LAYERS = [
    {"id": "secop", "name": "SECOP II y contratación pública", "required": True},
    {"id": "gobernacion", "name": "Gobernación y política territorial", "required": True},
    {"id": "distritos", "name": "Distrito / municipio sede", "required": True},
    {"id": "cultura", "name": "Consejerías o institutos de cultura", "required": True},
    {"id": "participacion", "name": "Participación, planeación y organizaciones", "required": True},
    {"id": "bancos", "name": "Bancos de proyectos, regalías y fondos", "required": True},
]


def norm(value):
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(ch for ch in text if not unicodedata.combining(ch)).lower().strip()


def canonical_department(value):
    candidate = norm(value)
    aliases = {
        "bogota d.c.": "Bogotá D.C.", "bogota": "Bogotá D.C.",
        "distrito capital de bogota": "Bogotá D.C.",
        "san andres y providencia": "San Andrés y Providencia",
        "san andres, providencia y santa catalina": "San Andrés y Providencia",
        "valle del cauca": "Valle del Cauca", "la guajira": "La Guajira",
    }
    if candidate in aliases:
        return aliases[candidate]
    for department in DEPARTMENTS:
        if norm(department) == candidate:
            return department
    return None


def evidence(department, layer, status, source="", url="", detail="", checked="2026-11-19"):
    return {
        "id": f"{norm(department).replace(' ', '-')}-{layer}",
        "department": department, "layer": layer, "status": status,
        "source": source, "url": url, "detail": detail, "checked": checked,
    }


def default_record(department):
    target = DEPARTMENT_TARGETS[department]
    return {
        "department": department,
        "identity": {"slug": target["slug"], "domain_hint": target["domain_hint"],
                     "seats": target.get("seats", []), "unified": bool(target.get("unified", False))},
        "evidence": [], "gaps": [layer["id"] for layer in LAYERS],
        "status": "pendiente", "notes": [],
    }


def add_evidence(records, department, layer, source, url, detail, status="hecha", checked="2026-11-19"):
    if department not in records:
        raise KeyError(f"Departamento fuera del censo: {department}")
    record = records[department]
    if layer not in {item["id"] for item in LAYERS}:
        raise KeyError(f"Capa desconocida: {layer}")
    if status not in {"hecha", "limitada", "pendiente", "sin_hallazgo"}:
        raise ValueError(f"Estado inválido: {status}")
    if not source or not detail or (status == "hecha" and not url):
        raise ValueError(f"Evidencia incompleta: {department} / {layer}")
    record["evidence"] = [item for item in record["evidence"] if item["layer"] != layer]
    record["evidence"].append(evidence(department, layer, status, source, url, detail, checked))
    if status == "hecha" and layer in record["gaps"]:
        record["gaps"].remove(layer)


def finalize(records):
    for record in records.values():
        present = {item["layer"] for item in record["evidence"] if item["status"] in ("hecha", "sin_hallazgo")}
        record["gaps"] = sorted({layer["id"] for layer in LAYERS} - present)
        record["reviewed"] = len(present)
        record["status"] = "cubierto" if not record["gaps"] else "pendiente"
    return records


def write_coverage(records, notes=None):
    payload = {
        "cutoff": "2026-11-19", "departments_count": len(records),
        "required_layers": LAYERS,
        "coverage_complete": all(record["status"] == "cubierto" for record in records.values()),
        "records": list(records.values()),
        "notes": notes or [],
    }
    COBERTURA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {
        "cutoff": payload["cutoff"], "departments_count": payload["departments_count"],
        "required_layers": LAYERS, "count": sum(len(record["evidence"]) for record in records.values()),
        "entries": [
            {"department": record["department"], **item}
            for record in records.values() for item in record["evidence"]
        ],
    }
    (RESEARCH / "source_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload
