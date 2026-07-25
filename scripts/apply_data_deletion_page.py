#!/usr/bin/env python3
"""Apply data-deletion page patches to dist/index.html only."""
from __future__ import annotations

import base64
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location(
    "patch_site_commercial", SCRIPTS / "patch-site-commercial.py"
)
patch_mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(patch_mod)

from data_deletion_request import patch_data_deletion_in_translations  # noqa: E402

INDEX = ROOT / "dist" / "index.html"


def main() -> None:
    html = INDEX.read_text()
    m = re.search(r'(<script type="importmap">)(.*?)(</script>)', html, re.S)
    assert m, "importmap not found"
    imap = json.loads(m.group(2))
    imports = imap["imports"]

    def get(key: str) -> str:
        return base64.b64decode(imports[key].split(",", 1)[1]).decode("utf-8")

    def set_(key: str, src: str) -> None:
        imports[key] = patch_mod.b64(src)

    set_("@/components/Footer", patch_mod.FOOTER_SRC)
    set_("@/components/DataDeletion", patch_mod.DATA_DELETION_SRC)
    set_("@/App", patch_mod.patch_app_data_deletion(get("@/App")))
    set_("@/seo", patch_mod.patch_seo_data_deletion(get("@/seo")))
    set_(
        "@/translations",
        patch_data_deletion_in_translations(get("@/translations")),
    )

    imap["imports"] = imports
    out = json.dumps(imap, separators=(",", ":"))
    INDEX.write_text(html[: m.start()] + m.group(1) + out + m.group(3) + html[m.end() :])
    print("data-deletion page patched", INDEX.stat().st_size)


if __name__ == "__main__":
    main()
