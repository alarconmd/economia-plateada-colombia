import csv
import json
import re
from html.parser import HTMLParser
from pathlib import Path

import pypdfium2 as pdfium
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "Informe_Economia_Plateada_Colombia_19NOV2026.pdf"
DATA = json.loads((ROOT / "research" / "dataset.json").read_text(encoding="utf-8"))
COV = json.loads((ROOT / "research" / "cobertura_territorial.json").read_text(encoding="utf-8"))
ITEMS, BASE, SECOP = DATA["items"], [x for x in DATA["items"] if not x.get("secop")], [x for x in DATA["items"] if x.get("secop")]


class Inspector(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.refs=[]; self.scripts=[]; self.styles=[]
    def handle_starttag(self, tag, attrs):
        values=dict(attrs)
        if values.get("id"): self.ids.append(values["id"])
        if tag=="script" and values.get("src"): self.scripts.append(values["src"])
        if tag=="link" and values.get("rel")=="stylesheet": self.styles.append(values.get("href"))
        for key in ("src","href"):
            value=values.get(key,"")
            if value and not value.startswith(("http://","https://","#","data:","mailto:","?")):
                self.refs.append(value)


reader=PdfReader(PDF)
texts=[page.extract_text() or "" for page in reader.pages]
full="\n".join(texts)
flat=re.sub(r"\s+"," ",full)
assert len(reader.pages)>=120, len(reader.pages)
for page in reader.pages:
    assert abs(float(page.mediabox.width)-595.28)<2 and abs(float(page.mediabox.height)-841.89)<2
assert all(len(text.strip())>40 for text in texts), [(i+1,len(t.strip())) for i,t in enumerate(texts) if len(t.strip())<=40]
missing_secop=[x["id_proceso"] for x in SECOP if x["id_proceso"] not in full]
assert not missing_secop, missing_secop[:10]
missing_base=[x["nombre"] for x in BASE if re.sub(r"\s+"," ",x["nombre"]) not in flat]
assert not missing_base, missing_base
for department in COV["records"]:
    assert department["department"] in full, department["department"]
uris=[]
for page in reader.pages:
    for reference in page.get("/Annots",[]):
        annotation=reference.get_object(); action=annotation.get("/A")
        if action and action.get("/URI"): uris.append(str(action.get("/URI")))
expected={source["url"] for item in BASE for source in item["fuentes"]}
expected |= {x["url"] for record in COV["records"] for x in record["evidence"] if x["url"]}
missing_urls=sorted(expected-set(uris))
# Los enlaces SECOP se verifican por su URL primaria, que también está en la tabla.
missing_secop_urls=sorted({x["fuentes"][0]["url"] for x in SECOP}-set(uris))
assert not missing_urls, missing_urls[:10]
assert not missing_secop_urls, missing_secop_urls[:10]
for relative in ["index.html","documento.html","cobertura.html","informe.css","oportunidades.csv","secop_oportunidades.csv","cobertura_territorial.json"]:
    assert (ROOT/relative).exists(), relative
with (ROOT/"oportunidades.csv").open(encoding="utf-8-sig",newline="") as handle:
    assert len(list(csv.DictReader(handle,delimiter=";")))==991
with (ROOT/"secop_oportunidades.csv").open(encoding="utf-8-sig",newline="") as handle:
    assert len(list(csv.DictReader(handle,delimiter=";")))==952
inspector=Inspector(); inspector.feed((ROOT/"index.html").read_text(encoding="utf-8"))
assert len(inspector.ids)==len(set(inspector.ids)), "IDs HTML duplicados"
assert not inspector.scripts and not inspector.styles, "Dependencias externas"
missing_refs=[ref for ref in inspector.refs if not (ROOT/ref.split("?")[0].split("#")[0]).exists()]
assert not missing_refs, missing_refs
render=[]
for index in sorted(set([0,1,len(reader.pages)//2,len(reader.pages)-1])):
    page=pdfium.PdfDocument(PDF)[index]
    path=ROOT/"research"/f"pdf_exhaustivo_pagina_{index+1:03d}.png"
    page.render(scale=1.3).to_pil().save(path)
    render.append(str(path))
report={
 "resultado":"APROBADO",
 "pdf":{"archivo":str(PDF),"bytes":PDF.stat().st_size,"paginas":len(reader.pages),"A4":True,
        "caracteres_minimos_pagina":min(len(t.strip()) for t in texts),"secop_ids":len(SECOP),
        "fichas_fuente":len(BASE),"territorios":len(COV["records"]),"enlaces_URI":len(uris),
        "enlaces_unicos":len(set(uris)),"fuentes_esperadas":len(expected)},
 "cobertura":{"departamentos":len(COV["records"]),"completos":sum(not r["gaps"] for r in COV["records"]),
              "evidencias":sum(len(r["evidence"]) for r in COV["records"]),
              "brechas":{r["department"]:r["gaps"] for r in COV["records"] if r["gaps"]}},
 "sitio":{"ids_html":len(inspector.ids),"recursos_locales":len(inspector.refs),"dependencias_externas":0,"registros":len(ITEMS)},
 "renderes":render,
}
(ROOT/"research"/"validacion_exhaustiva.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False,indent=2))
