import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
rows = json.loads((ROOT / "secop_crudo.json").read_text(encoding="utf-8"))
terms = ["persona mayor", "personas mayores", "adulto mayor", "adultos mayores", "envejecimiento", "vejez", "geriatr", "gerontolog", "longevidad", "cuidador", "centro vida", "centro día", "centro dia"]
offer_phases = {"Presentación de oferta", "Fase de Selección (Presentación de ofertas)", "Fase de ofertas", "Proceso de ofertas"}
selected = []
for row in rows:
    text = (row.get("nombre_del_procedimiento", "") + " " + row.get("descripci_n_del_procedimiento", "")).lower()
    if not any(term in text for term in terms):
        continue
    if row.get("fase") not in offer_phases or row.get("modalidad_de_contratacion") == "Contratación directa":
        continue
    if row.get("fecha_de_ultima_publicaci", "") < "2026-11-01":
        continue
    row["match"] = [term for term in terms if term in text]
    selected.append(row)
selected.sort(key=lambda row: row["precio_base"], reverse=True)
(ROOT / "secop_noviembre.json").write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding="utf-8")
lines=[]
for row in selected:
    lines.append("\t".join(str(row.get(k,"")).replace("\t"," ").replace("\n"," ") for k in ["id_del_proceso","referencia_del_proceso","entidad","departamento_entidad","ciudad_entidad","precio_base","modalidad_de_contratacion","fase","fecha_de_ultima_publicaci","nombre_del_procedimiento","urlproceso"]))
(ROOT / "secop_noviembre.tsv").write_text("\n".join(lines),encoding="utf-8")
print(f"Selección noviembre: {len(selected)} procesos")
print("\n".join(lines[:80]))
