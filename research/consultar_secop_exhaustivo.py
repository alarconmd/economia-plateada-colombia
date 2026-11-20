import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

OUT = Path(__file__).resolve().parent
API = "https://www.datos.gov.co/resource/p6dx-8zbt.json"
FIELDS = [
    "entidad", "nit_entidad", "departamento_entidad", "ciudad_entidad", "ordenentidad",
    "id_del_proceso", "referencia_del_proceso", "nombre_del_procedimiento",
    "descripci_n_del_procedimiento", "fase", "fecha_de_publicacion_del",
    "fecha_de_ultima_publicaci", "fecha_de_publicacion_fase_3", "precio_base",
    "modalidad_de_contratacion", "duracion", "unidad_de_duracion", "estado_del_procedimiento",
    "adjudicado", "estado_de_apertura_del_proceso", "tipo_de_contrato", "urlproceso", "estado_resumen",
]
# Se busca en nombre y descripción. Los términos sin tilde cubren errores comunes de carga.
TERMS = [
    "economía plateada", "economia plateada", "persona mayor", "personas mayores",
    "adulto mayor", "adultos mayores", "adulto myor", "envejecimiento", "envejecer",
    "vejez", "geriatr", "gerontolog", "longevidad", "mayores de 60", "60 años",
    "cuidador", "cuidadores", "cuidado", "centro vida", "centro día", "centro dia",
    "centros día", "centros dia", "pensionado", "pensionados", "dependencia funcional",
    "cuidado de larga duración", "cuidado de larga duracion", "protección social para la vejez",
    "salud del adulto", "salud de la vejez", "personas de edad avanzada", "tercera edad",
]
SINCE = "2026-01-01"
FRESHNESS = "2026-10-01"


def session():
    requests_session = requests.Session()
    retry = Retry(total=4, backoff_factor=1.5, status_forcelist=[429, 500, 502, 503, 504])
    requests_session.mount("https://", HTTPAdapter(max_retries=retry))
    return requests_session


def normalize(row):
    result = dict(row)
    url = result.get("urlproceso", "")
    if isinstance(url, dict):
        result["urlproceso"] = url.get("url", "")
    result["precio_base"] = int(float(result.get("precio_base") or 0))
    return result


def query(term, field, requests_session):
    where = (
        "estado_de_apertura_del_proceso='Abierto' AND estado_del_procedimiento='Publicado' "
        f"AND adjudicado='No' AND {field} >= '{SINCE}' AND lower({field}) like '%{term}%'"
    )
    params = {"$select": ",".join(FIELDS), "$where": where, "$limit": 5000,
              "$order": "fecha_de_ultima_publicaci DESC"}
    response = requests_session.get(API, params=params, timeout=120)
    response.raise_for_status()
    return term, field, [normalize(row) for row in response.json()]


def main():
    fields = ["nombre_del_procedimiento", "descripci_n_del_procedimiento"]
    found = {}
    matches = {}
    errors = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(query, term, field, session()) for term in TERMS for field in fields]
        for future in as_completed(futures):
            try:
                term, field, rows = future.result()
                matches[f"{field}:{term}"] = len(rows)
                for row in rows:
                    found[row["id_del_proceso"]] = row
                print(f"{field} · {term}: {len(rows)}", flush=True)
            except Exception as exc:
                errors.append(str(exc))
                print(f"ERROR: {exc}", flush=True)
    rows = sorted(found.values(), key=lambda row: row.get("fecha_de_ultima_publicaci", ""), reverse=True)
    cutoff = datetime.now(ZoneInfo("America/Bogota")).isoformat(timespec="seconds")
    metadata = {
        "fuente": "Colombia Compra Eficiente — SECOP II, Procesos de Contratación",
        "dataset": "p6dx-8zbt", "api": API, "corte_colombia": cutoff,
        "criterios": "abierto + publicado + no adjudicado + publicación desde 2026 + término en nombre o descripción",
        "desde": SINCE, "fecha_actualizacion_minima": FRESHNESS, "terminos": TERMS,
        "campos_consultados": fields, "registros": len(rows), "coincidencias": matches,
        "errores": errors, "advertencia": "Los registros abiertos no garantizan recepción vigente; ver pliegos y fecha de cierre.",
    }
    (OUT / "secop_exhaustivo.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "secop_exhaustivo_metadatos.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"corte": cutoff, "registros": len(rows), "errores": len(errors)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
