import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
rows = json.loads((ROOT / "secop_crudo.json").read_text(encoding="utf-8"))
terms = ["persona mayor", "personas mayores", "adulto mayor", "adultos mayores", "envejecimiento", "vejez", "geriatr", "gerontolog", "longevidad", "cuidador", "centro vida", "centro día", "centro dia", "pensionad"]
offer_phases = ["Presentación de oferta", "Fase de Selección (Presentación de ofertas)", "Fase de ofertas", "Proceso de ofertas"]
excluded_modalities = ["Contratación directa", "Mínima cuantía", "Concurso de méritos abierto con precalificación"]
for row in rows:
    text = (row.get("nombre_del_procedimiento", "") + " " + row.get("descripci_n_del_procedimiento", "")).lower()
    row["match"] = [term for term in terms if term in text]
    row["competitive"] = row.get("fase") in offer_phases and row.get("modalidad_de_contratacion") not in excluded_modalities
    row["bogota_cundinamarca"] = row.get("departamento_entidad") in ["Distrito Capital de Bogotá", "Cundinamarca"]
relevant = [row for row in rows if row["match"]]
print("TOTAL", len(rows), "RELEVANTES", len(relevant))
print("FASES", Counter(row.get("fase") for row in relevant))
print("MODALIDADES", Counter(row.get("modalidad_de_contratacion") for row in relevant))
sets = {
    "competitivos": sorted([r for r in relevant if r["competitive"]], key=lambda r:r["precio_base"], reverse=True),
    "bogota_cundinamarca": sorted([r for r in relevant if r["bogota_cundinamarca"]], key=lambda r:r.get("fecha_de_ultima_publicaci", ""), reverse=True),
}
for label, data in sets.items():
    print("\n###", label, len(data))
    for row in data[:100]:
        print(json.dumps({k:row.get(k) for k in ["id_del_proceso","referencia_del_proceso","entidad","departamento_entidad","ciudad_entidad","nombre_del_procedimiento","precio_base","modalidad_de_contratacion","fase","fecha_de_ultima_publicaci","urlproceso"]},ensure_ascii=False))
(ROOT / "secop_resumen.json").write_text(json.dumps({k:v for k,v in sets.items()},ensure_ascii=False,indent=2),encoding="utf-8")
