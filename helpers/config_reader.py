"""config_reader.py: Centralized config, prompt, YAML, and incidents loading."""

__author__ = "Praful"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"

import os
import yaml
from configparser import ConfigParser
from pathlib import Path
from typing import Any

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