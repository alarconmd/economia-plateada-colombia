import json
from pathlib import Path

import pypdf
import requests
import urllib3

urllib3.disable_warnings()
OUT = Path(__file__).resolve().parent / "fuentes_pdf"
OUT.mkdir(exist_ok=True)
SOURCES = {
    "caf_lif_2026": "https://www.caf.com/media/4687951/bases-lif-2026-es.pdf",
    "sgr_anexo_15_acuerdo_18_2026": "https://colaboracion.dnp.gov.co/CDT/Sistema%20General%20de%20las%20Regalas%20SGR/Normativa/actas-acuerdos/acuerdo-18-comision-rectora-2026-07-31.pdf",
    "ocad_paz_tdr_convocatorias_2_3_4": "https://colaboracion.dnp.gov.co/CDT/Sistema%20General%20de%20las%20Regalas%20SGR/Convocatorias/terminos-de-referencia-convocatoria-2-3-4-ocad-paz-bienio-2025-2026-02-23.pdf",
    "ocad_paz_guia_convocatoria_3": "https://colaboracion.dnp.gov.co/CDT/Sistema%20General%20de%20las%20Regalas%20SGR/Convocatorias/guia-postulacion-proyectos-convocatoria-3-ocad-paz-bienio-2025-2026.pdf",
}
index=[]
for name,url in SOURCES.items():
    try:
        response=requests.get(url,timeout=120,verify=False,headers={"User-Agent":"Mozilla/5.0"})
        item={"nombre":name,"url":url,"http":response.status_code,"tipo":response.headers.get("content-type"),"bytes":len(response.content)}
        if response.ok and response.content.startswith(b"%PDF"):
            path=OUT/(name+".pdf")
            path.write_bytes(response.content)
            reader=pypdf.PdfReader(path)
            text="\n\n".join(page.extract_text() or "" for page in reader.pages)
            (OUT/(name+".txt")).write_text(text,encoding="utf-8")
            item.update({"paginas":len(reader.pages),"caracteres":len(text),"archivo":str(path)})
        else:
            item["inicio"]=response.text[:300]
        index.append(item)
        print(json.dumps(item,ensure_ascii=False),flush=True)
    except Exception as exc:
        index.append({"nombre":name,"url":url,"error":str(exc)})
        print(name,exc,flush=True)
(OUT/"indice.json").write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf-8")
