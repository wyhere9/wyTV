from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str | Path) -> dict[str, Any]:
    p = ROOT / path if not Path(path).is_absolute() else Path(path)
    with p.open('r', encoding='utf-8') as f:
        return json.load(f)


def ensure_dirs() -> None:
    (ROOT / 'output').mkdir(exist_ok=True)
