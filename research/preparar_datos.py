import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
BASE = json.loads((RESEARCH / "oportunidades_base.json").read_text(encoding="utf-8"))
SECOP = json.loads((RESEARCH / "secop_noviembre.json").read_text(encoding="utf-8"))
DATASET_URL = "https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt/about_data"
ADJACENT = {"CO1.REQ.11376047", "CO1.REQ.11309230", "CO1.REQ.11385969"}


def money(value):
    if not value:
        return "Sin precio base publicado"
    return "$" + f"{value:,.0f}".replace(",", ".") + " COP"


def theme(text):
    rules = [
        (["construcción", "adecuacion", "adecuación", "cubierta"], "Infraestructura y accesibilidad"),
        (["alimentación", "alimentacion", "paquetes nutricionales"], "Alimentación"),
        (["geriatr", "rehabilitacion", "rehabilitación", "medicina", "salud"], "Salud y geriatría"),
        (["política pública", "politica publica"], "Política pública"),
        (["transporte"], "Movilidad y cuidado"),
        (["atención", "atencion", "centro vida", "centro de protección", "casa del adulto"], "Operación de cuidado"),
    ]
    for words, label in rules:
        if any(word in text for word in words):
            return label
    return "Participación y logística"


def convert(row):
    process_id = row["id_del_proceso"]
    object_text = row["nombre_del_procedimiento"]
    text = (object_text + " " + row.get("descripci_n_del_procedimiento", "")).lower()
    dept = row.get("departamento_entidad", "No definido")
    city = row.get("ciudad_entidad", "No definido")
    cap = 1 if dept in {"Distrito Capital de Bogotá", "Cundinamarca"} else 2
    topic = theme(text)
    adjacent = process_id in ADJACENT
    return {
        "id": "secop-" + process_id.replace("CO1.REQ.", ""), "cap": cap,
        "nombre": object_text, "entidad": row["entidad"], "territorio": f"{city} / {dept}",
        "tipo": "Contratación pública SECOP II", "estado": "secop",
        "objetivo": object_text,
        "encaje": ("Oportunidad adyacente de economía del cuidado; no está centrada exclusivamente en personas mayores. " if adjacent else "Relación explícita con personas mayores, envejecimiento o cuidado. ") + "Es contratación: el oferente cobra por ejecutar el objeto y debe acreditar las condiciones del pliego; no es financiación a una iniciativa propia.",
        "postulantes": ["Proveedores u operadores que cumplan el aviso, habilitación, experiencia y capacidad exigidos"],
        "requisitos": ["Cuenta de proveedor SECOP II y RUP cuando sea exigible", "Revisar pliego, estudios previos, anexos y adendas", "Acreditar experiencia, capacidad técnica/financiera, garantías y documentos específicos", "Presentar oferta electrónica antes del cierre", "Confirmar cierre y lugar de ejecución: el dataset no expone la fecha/hora límite"],
        "presencia": f"Oferta digital. La ejecución parece vinculada a {city} / {dept}, pero el lugar exacto, visitas y obligaciones presenciales deben confirmarse en el expediente.",
        "canal": f"SECOP II · {row.get('fase')} · {row.get('modalidad_de_contratacion')} · actualización {row.get('fecha_de_ultima_publicaci', '')[:10]}",
        "fuentes": [{"titulo": f"Aviso SECOP {row.get('referencia_del_proceso')}", "url": row["urlproceso"]}, {"titulo": "Dataset oficial p6dx-8zbt", "url": DATASET_URL}],
        "monto": money(row.get("precio_base", 0)), "cierre": "No expuesto en el dataset; confirmar hoy en el aviso",
        "prioridad": "Media" if adjacent else "Alta", "temas": [topic, "SECOP II", "Cuidado adyacente" if adjacent else "Personas mayores"],
        "accion": "Abrir el aviso, descargar documentos y verificar cierre antes de asignar equipo o preparar oferta.",
        "nota": "El registro figura publicado, abierto, no adjudicado y actualizado en noviembre de 2026. Esto no garantiza que la recepción siga habilitada; la ficha SECOP puede solicitar captcha.",
        "secop": True, "id_proceso": process_id, "referencia": row.get("referencia_del_proceso"),
        "precio_num": row.get("precio_base", 0), "actualizacion": row.get("fecha_de_ultima_publicaci"),
        "fase": row.get("fase"), "modalidad": row.get("modalidad_de_contratacion"),
        "departamento": dept, "ciudad": city, "descripcion": row.get("descripci_n_del_procedimiento", ""),
    }


def main():
    secop_items = [convert(row) for row in SECOP]
    items = BASE + secop_items
    ids = [item["id"] for item in items]
    assert len(ids) == len(set(ids)), "IDs duplicados"
    for item in items:
        for field in ["nombre", "entidad", "objetivo", "encaje", "postulantes", "requisitos", "presencia", "canal", "fuentes", "accion"]:
            assert item.get(field), (item["id"], field)
        assert all(source["url"].startswith(("http://", "https://")) for source in item["fuentes"])
    payload = {"corte": "19 de noviembre de 2026", "corte_secop": "2026-11-19 09:32:12 (hora Colombia)",
               "total": len(items), "base": len(BASE), "secop": len(secop_items), "items": items}
    (RESEARCH / "dataset.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = ["id", "cap", "nombre", "entidad", "territorio", "tipo", "estado", "monto", "cierre", "prioridad", "temas", "presencia", "accion"]
    with (ROOT / "oportunidades.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        for item in items:
            row = dict(item); row["temas"] = " | ".join(item["temas"]); writer.writerow(row)
    print(json.dumps({"total": len(items), "base": len(BASE), "secop": len(secop_items)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
