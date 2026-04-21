"""constants.py: Application constants"""

__author__ = "Praful"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"

import json
import re
from pathlib import Path

AZURE_OPENAI_API_KEY = 'AZURE_OPENAI_API_KEY'
AZURE_OPENAI_ENDPOINT = 'AZURE_OPENAI_ENDPOINT'
AZURE_OPENAI_MODEL = 'AZURE_OPENAI_MODEL'
AZURE_OPENAI_API_VERSION = 'AZURE_OPENAI_API_VERSION'

AZURE_OPEN_AI_DEFAULT_MODEL_NAME = 'gpt-4o'
AZURE_OPEN_AI_DEFAULT_VERSION = '2025-01-01-preview'

OUTPUT_PAYLOAD_PATH = "./output_files/output_payload.json"
OUTPUT_RULES_PATH = "./output_files/output_rules.json"
OUTPUT_AGENT_PATH = "./output_files/agent_output.json"
MASTER_RULES_PATH = "./master_rules/master_transformation_rules.json"
TASKS_CONFIG_PATH = "./config/tasks.yaml"
AGENTS_CONFIG_PATH = "./config/agents.yaml"

PAYLOAD_MAPPING_PROMPT = 'payload_mapping_prompt'
DT_RULE_GENERATION_PROMPT = 'rule_generation_prompt'
VALIDIO_DT_RULE_GENERATION_PROMPT = 'validio_rule_generation_prompt'

VALIDIO = 'validio'


def save_json(path: str, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_parse_json(raw_text: str):
    if not raw_text or not raw_text.strip():
        raise ValueError("Input is empty.")

    raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    cleaned = re.sub(r"^```json\s*", "", raw_text, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```", "", cleaned)
    cleaned = re.sub(r"```$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON even after cleaning: {e}")
