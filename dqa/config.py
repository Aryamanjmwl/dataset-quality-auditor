from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass(frozen=True)
class Config:
    """
    Simple config container for audit params.
    """

    params: Dict[str, Any]

    @staticmethod
    def load(path: str | Path) -> "Config":
        p = Path(path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {p}")

        if p.suffix.lower() in {".yml", ".yaml"}:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        elif p.suffix.lower() == ".json":
            data = json.loads(p.read_text(encoding="utf-8"))
        else:
            raise ValueError("Config must be .yaml/.yml or .json")

        if not isinstance(data, dict):
            raise ValueError("Config root must be a mapping/dict")

        params = data.get("params", data)
        if not isinstance(params, dict):
            raise ValueError("Config params must be a dict")

        return Config(params=params)


def merge_params(
    base: Optional[Dict[str, Any]],
    override: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Merge two dicts shallowly: override wins.
    """
    out: Dict[str, Any] = {}
    if base:
        out.update(base)
    if override:
        out.update(override)
    return out
