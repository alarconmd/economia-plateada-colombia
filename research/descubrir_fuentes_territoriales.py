import json
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings()
RESEARCH = Path(__file__).resolve().parent
RESULTS = RESEARCH / "fuentes_territoriales_crudo.json"

GOVERNORATES = {
    "Amazonas": ["https://www.gubernaciondeamazonas.gov.co/", "https://amazonas.gov.co/"],
    "Antioquia": ["https://www.antioquia.gov.co/"],
    "Arauca": ["https://www.arauca.gov.co/", "https://www.gobernaciondearauca.gov.co/"],
    "Atlántico": ["https://www.atlantico.gov.co/"],
    "Bogotá D.C.": ["https://bogota.gov.co/"],
    "Bolívar": ["https://www.bolivar.gov.co/"],
    "Boyacá": ["https://www.boyaca.gov.co/"],
    "Caldas": ["https://www.caldas.gov.co/"],
    "Caquetá": ["https://www.caqueta.gov.co/"],
    "Casanare": ["https://www.casanare.gov.co/"],
    "Cauca": ["https://www.cauca.gov.co/"],
    "Cesar": ["https://cesar.gov.co/d/", "https://www.cesar.gov.co/"],
    "Chocó": ["https://www.choco.gov.co/"],
    "Córdoba": ["https://www.cordoba.gov.co/"],
    "Cundinamarca": ["https://www.cundinamarca.gov.co/"],
    "Guainía": ["https://www.guainia.gov.co/"],
    "Guaviare": ["https://www.guaviare.gov.co/"],
    "Huila": ["https://www.huila.gov.co/"],
    "La Guajira": ["https://www.laguajira.gov.co/"],
    "Magdalena": ["https://www.gobernaciondelmagdalena.gov.co/", "https://www.magdalena.gov.co/"],
    "Meta": ["https://meta.gov.co/"],
    "Nariño": ["https://www.narino.gov.co/"],
    "Norte de Santander": ["https://www.nortedesantander.gov.co/"],
    "Putumayo": ["https://www.putumayo.gov.co/"],
    "Quindío": ["https://www.quindio.gov.co/"],
    "Risaralda": ["https://www.risaralda.gov.co/"],
    "San Andrés y Providencia": ["https://www.sanandres.gov.co/"],
    "Santander": ["https://www.santander.gov.co/"],
    "Sucre": ["https://www.sucre.gov.co/"],
    "Tolima": ["https://www.tolima.gov.co/"],
    "Valle del Cauca": ["https://www.valledelcauca.gov.co/"],
    "Vaupés": ["https://www.vaupes.gov.co/"],
    "Vichada": ["https://www.vichada.gov.co/"],
}

CAPITALS = {
    "Amazonas": [("Leticia", "https://www.leticia-amazonas.gov.co/")],
    "Antioquia": [("Medellín", "https://www.medellin.gov.co/")],
    "Arauca": [("Arauca", "https://www.arauca.gov.co/")],
    "Atlántico": [("Barranquilla", "https://www.barranquilla.gov.co/")],
    "Bogotá D.C.": [("Bogotá", "https://bogota.gov.co/")],
    "Bolívar": [("Cartagena", "https://www.cartagena.gov.co/")],
    "Boyacá": [("Tunja", "https://www.tunja-boyaca.gov.co/")],
    "Caldas": [("Manizales", "https://www.manizales.gov.co/")],
    "Caquetá": [("Florencia", "https://www.florencia-caqueta.gov.co/")],
    "Casanare": [("Yopal", "https://www.yopal.gov.co/")],
    "Cauca": [("Popayán", "https://www.popayan.gov.co/")],
    "Cesar": [("Valledupar", "https://www.valledupar-cesar.gov.co/")],
    "Chocó": [("Quibdó", "https://www.quibdo-choco.gov.co/")],
    "Córdoba": [("Montería", "https://www.monteria.gov.co/")],
    "Cundinamarca": [("Bogotá", "https://bogota.gov.co/")],
    "Guainía": [("Inírida", "https://www.inirida-guainia.gov.co/")],
    "Guaviare": [("San José del Guaviare", "https://www.sanjosedelguaviare-guaviare.gov.co/")],
    "Huila": [("Neiva", "https://www.alcaldianeiva.gov.co/")],
    "La Guajira": [("Riohacha", "https://www.riohacha-laguajira.gov.co/")],
    "Magdalena": [("Santa Marta", "https://www.santamarta.gov.co/")],
    "Meta": [("Villavicencio", "https://www.villavicencio.gov.co/")],
    "Nariño": [("Pasto", "https://www.pasto.gov.co/")],
    "Norte de Santander": [("Cúcuta", "https://cucuta.gov.co/")],
    "Putumayo": [("Mocoa", "https://www.mocoa-putumayo.gov.co/")],
    "Quindío": [("Armenia", "https://www.armenia.gov.co/")],
    "Risaralda": [("Pereira", "https://www.pereira.gov.co/")],
    "San Andrés y Providencia": [("San Andrés", "https://www.sanandres.gov.co/")],
    "Santander": [("Bucaramanga", "https://www.bucaramanga.gov.co/")],
    "Sucre": [("Sincelejo", "https://www.alcaldiadesincelejo.gov.co/")],
    "Tolima": [("Ibagué", "https://www.ibague.gov.co/")],
    "Valle del Cauca": [("Cali", "https://www.cali.gov.co/")],
    "Vaupés": [("Mitú", "https://www.mitu-vaupes.gov.co/")],
    "Vichada": [("Puerto Carreño", "https://www.puertocarreno-vichada.gov.co/")],
}

KEYWORDS = {
    "cultura": ["cultura", "instituto de cultura", "secretaria de cultura", "consejeria de cultura"],
    "participacion": ["participacion", "participativo", "accion comunal", "planeacion", "consejo de politica social"],
    "bancos": ["regalia", "banco de proyectos", "presupuesto", "convocatoria", "fondo", "proyecto"],
    "older": ["adulto mayor", "persona mayor", "personas mayores", "envejecimiento", "vejez", "centro dia", "centro vida"],
}
def fetch(url):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; ObservatorioEconomiaPlateada/1.0; +https://github.com/alarconmd/economia-plateada-colombia)"})
    try:
        response = session.get(url, timeout=15, verify=False, allow_redirects=True)
        soup = BeautifulSoup(response.text[:700000], "lxml")
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        links = []
        for anchor in soup.find_all("a", href=True):
            href = urljoin(response.url, anchor.get("href", "").strip())
            text = anchor.get_text(" ", strip=True)
            if href.startswith(("http://", "https://")) and text:
                links.append({"text": text[:180], "url": href})
        return {"seed": url, "final_url": response.url, "status": response.status_code,
                "content_type": response.headers.get("content-type", ""), "title": title,
                "links": links, "error": ""}
    except Exception as exc:
        return {"seed": url, "final_url": "", "status": None, "content_type": "",
                "title": "", "links": [], "error": str(exc)[:500]}


def matches(links, words):
    found = {}
    for link in links:
        searchable = (link["text"] + " " + urlparse(link["url"]).path).lower()
        for word in words:
            if word in searchable:
                found.setdefault(word, [])
                if len(found[word]) < 8 and link not in found[word]:
                    found[word].append(link)
    return found


def main():
    jobs = [(department, "gobernacion", seeds) for department, seeds in GOVERNORATES.items()]
    jobs += [(department, "distritos", [capital[1] for capital in capitals]) for department, capitals in CAPITALS.items()]
    unique_seeds = sorted({seed for _, _, seeds in jobs for seed in seeds})
    pages = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch, seed): seed for seed in unique_seeds}
        for future in as_completed(futures):
            result = future.result()
            pages[result["seed"]] = result
            print(f"{result['status']} {result['seed']} {result['title'][:70]}", flush=True)
    records = []
    for department, layer, seeds in jobs:
        result = next((pages[seed] for seed in seeds if pages[seed]["status"] == 200), None)
        records.append({
            "department": department, "layer": layer, "result": result,
            "matches": matches(result["links"], [w for group in KEYWORDS.values() for w in group]) if result else {},
        })
    RESULTS.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "urls_probadas": len(pages), "registros": len(records),
        "gobernaciones_ok": sum(1 for r in records if r["layer"] == "gobernacion" and r["result"]),
        "capitales_ok": sum(1 for r in records if r["layer"] == "distritos" and r["result"]),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
