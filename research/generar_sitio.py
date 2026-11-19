import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = (ROOT / "research" / "dataset.json").read_text(encoding="utf-8")
# Evita que contenido textual pueda cerrar el script en HTML.
data = data.replace("</", "<\\/")
template = (ROOT / "research" / "plantilla_sitio.html").read_text(encoding="utf-8")
assert "__DATA_JSON__" in template
assert "__SCRIPT" not in template.replace("__DATA_JSON__", "")
output = template.replace("__DATA_JSON__", data)
(ROOT / "index.html").write_text(output, encoding="utf-8")
print(json.dumps({"archivo": str(ROOT / "index.html"), "bytes": (ROOT / "index.html").stat().st_size}, ensure_ascii=False))
