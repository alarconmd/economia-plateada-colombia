import json
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent
COBERTURA = ROOT / "cobertura_territorial.json"
OUTPUT = ROOT / "fuentes_sitemaps.json"

GROUPS = {
    "cultura": ["cultura", "patrimonio", "estímulo", "estimulo", "convocatoria-cultural"],
    "participacion": ["participacion", "participación", "participativo", "planeacion", "planeación", "accion-comunal", "consejo-mayor", "consejo-de-sabios"],
    "bancos": ["regalia", "regalía", "banco-de-proyectos", "banco-proyectos", "presupuesto", "convocatoria", "fondo"],
}
SITEMAP_PATHS = ["sitemap.xml", "sitemap_index.xml", "wp-sitemap.xml", "sitemap-index.xml", "?sitemap=index"]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ObservatorioEconomiaPlateada/1.0)"}


def fetch_text(url):
    try:
        response = requests.get(url, timeout=20, verify=False, headers=HEADERS)
        if response.status_code != 200:
            return None
        return response.text[:2000000]
    except Exception:
        return None


def sitemap_urls(url, depth=0):
    text = fetch_text(url)
    if not text or "<" not in text[:200]:
        return []
    soup = BeautifulSoup(text, "xml")
    locs = [tag.get_text(strip=True) for tag in soup.find_all("loc")]
    urls = []
    children = []
    for loc in locs:
        if loc.endswith(".xml") or "sitemap" in loc.lower():
            children.append(loc)
        elif loc.startswith("http"):
            urls.append(loc)
    if depth < 2:
        for child in children[:12]:
            urls.extend(sitemap_urls(child, depth + 1))
    return urls


def discover(record):
    department = record["department"]
    root = next((item["url"] for item in record["evidence"] if item["layer"] in ("gobernacion", "distritos") and item["status"] == "hecha" and item["url"]), "")
    result = {"department": department, "root": root, "sitemaps_ok": [], "matches": {key: [] for key in GROUPS}, "errors": []}
    if not root:
        result["errors"].append("Sin portal raíz verificado")
        return result
    candidates = [urljoin(root, path) for path in SITEMAP_PATHS]
    for sitemap in candidates:
        text = fetch_text(sitemap)
        if not text or "<loc" not in text:
            continue
        result["sitemaps_ok"].append(sitemap)
        soup = BeautifulSoup(text, "xml")
        locs = [tag.get_text(strip=True) for tag in soup.find_all("loc")]
        children = [loc for loc in locs if loc.endswith(".xml") or "sitemap" in loc.lower()]
        pages = [loc for loc in locs if loc.startswith("http") and loc not in children]
        for child in children[:8]:
            pages.extend(sitemap_urls(child))
        for key, words in GROUPS.items():
            for page in pages:
                normalized = page.lower()
                if any(word in normalized for word in words):
                    if page not in result["matches"][key]:
                        result["matches"][key].append(page)
                    if len(result["matches"][key]) >= 12:
                        break
        if any(result["matches"].values()):
            break
    return result


def main():
    payload = json.loads(COBERTURA.read_text(encoding="utf-8"))
    records = payload["records"]
    results = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(discover, record): record["department"] for record in records}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"{result['department']}: sitemaps={len(result['sitemaps_ok'])} matches={sum(bool(v) for v in result['matches'].values())}", flush=True)
    results.sort(key=lambda item: item["department"])
    OUTPUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"sitios": len(results), "con_sitemap": sum(bool(x["sitemaps_ok"]) for x in results), "con_match": sum(any(x["matches"].values()) for x in results)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
