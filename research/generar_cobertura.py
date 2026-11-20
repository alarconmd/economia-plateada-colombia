import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
coverage_path = ROOT / "research" / "cobertura_territorial.json"
manifest_path = ROOT / "research" / "source_manifest.json"
shutil.copyfile(coverage_path, ROOT / "cobertura_territorial.json")
shutil.copyfile(manifest_path, ROOT / "source_manifest.json")
coverage = coverage_path.read_text(encoding="utf-8").replace("</", "<\\/")
template = (ROOT / "research" / "plantilla_cobertura.html").read_text(encoding="utf-8")
assert "__COVERAGE_JSON__" in template
output = template.replace("__COVERAGE_JSON__", coverage)
assert "__SCRIPT__" not in output
(ROOT / "cobertura.html").write_text(output, encoding="utf-8")
print(json.dumps({"archivo": str(ROOT / "cobertura.html"), "bytes": len(output.encode("utf-8"))}, ensure_ascii=False))
