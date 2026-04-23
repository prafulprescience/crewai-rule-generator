"""config_reader.py: Centralized config, prompt, YAML, and incidents loading."""

__author__ = "Praful"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"

import os
from configparser import ConfigParser
from pathlib import Path
from typing import Any, Optional

import yaml

from constants import VALIDIO, load_json

current_dir = Path(__file__).parent
project_root = current_dir.parent

PROMPT_FILE_PATH = os.path.join(project_root, "config", "prompts.ini")

_CONFIG = ConfigParser(interpolation=None)
_CONFIG.read(PROMPT_FILE_PATH, encoding="utf-8")

DEFAULT_CONFIG_SECTION = "config"


def get_prompt(prompt_name: str) -> str:
    if DEFAULT_CONFIG_SECTION not in _CONFIG:
        raise KeyError(
            f"Prompt section '{DEFAULT_CONFIG_SECTION}' not found in prompts.ini. "
            f"Available sections: {_CONFIG.sections()}"
        )

    return _CONFIG[DEFAULT_CONFIG_SECTION][prompt_name]


def load_yaml(path: str | Path) -> Any:
    p = Path(path)
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_incidents_bundle(incident_type: Optional[str]) -> dict[str, Any]:
    base = (
        Path("./incidents/validio_incidents")
        if incident_type == VALIDIO
        else Path("./incidents/general_incidents")
    )
    incidents: list[dict[str, Any]] = []
    if not base.is_dir():
        return {
            "incident_type": incident_type or "general",
            "error": f"Incident directory not found: {base}",
            "count": 0,
            "incidents": incidents,
        }
    for path in sorted(base.glob("incident_*.json")):
        try:
            incidents.append(
                {
                    "file_name": path.name,
                    "path": str(path),
                    "data": load_json(str(path)),
                }
            )
        except Exception as e:
            incidents.append(
                {"file_name": path.name, "path": str(path), "error": str(e)}
            )
    return {
        "incident_type": incident_type or "general",
        "count": len(incidents),
        "incidents": incidents,
    }
