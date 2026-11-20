import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROWS = json.loads((ROOT / "secop_exhaustivo.json").read_text(encoding="utf-8"))
STRONG = [
    "economía plateada", "economia plateada", "persona mayor", "personas mayores",
    "adulto mayor", "adultos mayores", "envejecimiento", "vejez", "geriatr",
    "gerontolog", "longevidad", "cuidador", "cuidadores", "centro vida",
    "centro día", "centro dia", "centros día", "centros dia", "pensionado",
    "pensionados", "tercera edad", "salud del adulto", "mayores de 60",
    "60 o más", "edad avanzada", "adultez y vejez", "dependencia funcional",
]
WEAK = ["cuidado", "60 años", "discapacidad"]
OFFER = {"Presentación de oferta", "Fase de Selección (Presentación de ofertas)", "Fase de ofertas", "Proceso de ofertas", "Manifestación de interés (Menor Cuantía)"}
FRESH = "2026-10-01"


def text(row):
    return (row.get("nombre_del_procedimiento", "") + " " + row.get("descripci_n_del_procedimiento", "")).lower()


def classify(row):
    value = text(row)
    return [term for term in STRONG if term in value], [term for term in WEAK if term in value]


def keep(row):
    strong, weak = classify(row)
    return bool(strong or weak) and row.get("fase") in OFFER and row.get("modalidad_de_contratacion") != "Contratación directa" and row.get("fecha_de_ultima_publicaci", "") >= FRESH


selected = [row for row in ROWS if keep(row)]
for row in selected:
    row["match_directo"], row["match_interseccion"] = classify(row)
selected.sort(key=lambda row: (row.get("fecha_de_ultima_publicaci", ""), row.get("precio_base", 0)), reverse=True)
meta = {
    "corte": "2026-11-19", "dataset": "p6dx-8zbt", "consultados": len(ROWS),
    "seleccion": len(selected), "directos": sum(bool(row["match_directo"]) for row in selected),
    "solo_interseccion": sum(not row["match_directo"] for row in selected),
    "noviembre": sum(row.get("fecha_de_ultima_publicaci", "") >= "2026-11-01" for row in selected),
    "departamentos": dict(Counter(row.get("departamento_entidad") for row in selected)),
    "advertencia": "Candidatura temática; cierre y recepción se confirman en cada aviso SECOP.",
}
(ROOT / "secop_exhaustivo_seleccion.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "secop_exhaustivo_seleccion_metadatos.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(meta, ensure_ascii=False, indent=2))


