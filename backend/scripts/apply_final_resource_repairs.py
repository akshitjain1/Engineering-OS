from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from app.content.final_resource_repairs import apply_final_resource_repairs
from app.db.session import SessionLocal

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "dev.db"


def main() -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / f"dev.db.pre_final_resource_repairs_{ts}.bak"
    shutil.copy2(DB_PATH, backup)
    db = SessionLocal()
    try:
        result = apply_final_resource_repairs(db)
        report = {"backup": str(backup), **result}
        out = ROOT / "reports" / "final_resource_repairs_apply.json"
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"backup": str(backup), "updated": result["updated"], "missing": result["missing"]}, indent=2))
        if result["missing"]:
            raise SystemExit("Missing resource slugs: " + ", ".join(result["missing"]))
    finally:
        db.close()


if __name__ == "__main__":
    main()
