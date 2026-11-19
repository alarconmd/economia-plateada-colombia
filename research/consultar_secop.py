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
    "entidad", "nit_entidad", "departamento_entidad", "ciudad_entidad",
    "id_del_proceso", "referencia_del_proceso", "nombre_del_procedimiento",
    "descripci_n_del_procedimiento", "fase", "fecha_de_publicacion_del",
    "fecha_de_ultima_publicaci", "precio_base", "modalidad_de_contratacion",
    "duracion", "unidad_de_duracion", "estado_del_procedimiento", "adjudicado",
    "estado_de_apertura_del_proceso", "tipo_de_contrato", "urlproceso",
    "estado_resumen",
]
TERMS = [
    "economía plateada", "economia plateada", "persona mayor", "personas mayores",
    "adulto mayor", "adultos mayores", "envejecimiento", "vejez", "geriatr",
    "gerontolog", "longevidad", "cuidador", "cuidadores", "centro vida",
    "centro día", "centros día", "centro dia", "centros dia", "pensionado",
    "pensionados", "dependencia funcional", "cuidado de larga duración",
    "cuidado de larga duracion", "protección social para la vejez",
]


def fetch(term):
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    base = "estado_de_apertura_del_proceso='Abierto' AND estado_del_procedimiento='Publicado' AND adjudicado='No'"
    where = f"{base} AND lower(nombre_del_procedimiento) like '%{term}%'"
    params = {
        "$select": ",".join(FIELDS), "$where": where, "$limit": 5000,
        "$order": "fecha_de_ultima_publicaci DESC",
    }
    response = session.get(API, params=params, timeout=90)
    response.raise_for_status()
    return term, response.json()


def normalize(row):
    result = dict(row)
    url = result.get("urlproceso", "")
    if isinstance(url, dict):
        result["urlproceso"] = url.get("url", "")
    result["precio_base"] = int(float(result.get("precio_base") or 0))
    return result


def main():
    base = "estado_de_apertura_del_proceso='Abierto' AND estado_del_procedimiento='Publicado' AND adjudicado='No'"
    found = {}
    matches = {}
    errors = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch, term): term for term in TERMS}
        for future in as_completed(futures):
            term = futures[future]
            try:
                _, data = future.result()
                matches[term] = len(data)
                for row in data:
                    normalized = normalize(row)
                    found[normalized["id_del_proceso"]] = normalized
                print(f"{term}: {len(data)}", flush=True)
            except Exception as exc:
                errors[term] = str(exc)
                print(f"ERROR {term}: {exc}", flush=True)
    rows = sorted(found.values(), key=lambda row: row.get("fecha_de_ultima_publicaci", ""), reverse=True)
    cutoff = datetime.now(ZoneInfo("America/Bogota")).isoformat(timespec="seconds")
    metadata = {
        "fuente": "Colombia Compra Eficiente — SECOP II, Procesos de Contratación",
        "dataset": "p6dx-8zbt",
        "api": API,
        "corte_colombia": cutoff,
        "criterios": base,
        "terminos": TERMS,
        "registros": len(rows), "coincidencias_por_termino": matches, "errores": errors,
        "alcance_busqueda": "Coincidencia en nombre_del_procedimiento; la descripción se conserva para depuración.",
        "advertencia": "Consulta por palabras clave; requiere depuración y verificación de pliegos y cronograma en cada aviso.",
    }
    (OUT / "secop_crudo.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "secop_metadatos.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUT / "secop_crudo.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore", delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"corte": cutoff, "registros": len(rows), "archivo": str(OUT / 'secop_crudo.csv')}, ensure_ascii=False))


if __name__ == "__main__":
    main()
