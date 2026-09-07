"""Export the actual application schema; offline defaults are not credentials."""
import os
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for name in ("GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO", "WEBHOOK_SECRET"):
    os.environ.setdefault(name, "schema-export-placeholder")
from app.main import app  # noqa: E402

(ROOT / "openapi.yaml").write_text(yaml.safe_dump(app.openapi(), sort_keys=False))
print("Exported openapi.yaml from the application")
