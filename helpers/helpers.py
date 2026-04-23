"""helpers.py: Helpers for agentic rule generation"""

__author__ = "Prajeesh"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"

from constants import (
    DQ_RULE_GENERATION_PROMPT,
    DT_RULE_GENERATION_PROMPT,
    MASTER_DQ_RULES_PATH,
    MASTER_DT_RULES_PATH,
    OUTPUT_AGENT_PATH,
    DATA_QUALITY,
    load_json,
    safe_parse_json,
    save_json,
)
from typing import Optional
from helpers.config_reader import get_prompt


def fill_ini_prompt_placeholders(
    template: str,
    *,
    incident_json: Optional[str] = None,
    master_rules: Optional[str] = None,
    ds_info: Optional[str] = None,
    data_profile: Optional[str] = None,
    additional_info: Optional[str] = None,
    generated_rule: Optional[str] = None,
    existing_payload: Optional[str] = None,
) -> str:
    out = template
    if incident_json is not None:
        out = out.replace("{incident_json}", incident_json)
    if master_rules is not None:
        out = out.replace("{master_rules}", master_rules)
    if ds_info is not None:
        out = out.replace("{ds_info}", ds_info)
    if data_profile is not None:
        out = out.replace("{data_profile}", data_profile)
    if additional_info is not None:
        out = out.replace("{additional_info}", additional_info)
    if generated_rule is not None:
        out = out.replace("{generated_rule}", generated_rule)
    if existing_payload is not None:
        out = out.replace("{existing_payload}", existing_payload)
    return out


def make_json_safe(obj):
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        return str(obj)
    

def extract_agent_output(result):
    outputs = []

    if hasattr(result, "tasks_output"):
        for i, task_out in enumerate(result.tasks_output, start=1):
            raw = getattr(task_out, "raw", None)

            parsed = None
            if raw:
                try:
                    parsed = safe_parse_json(raw)
                except Exception:
                    parsed = None  # don't break if parsing fails

            outputs.append({
                "task_index": i,
                "agent": str(getattr(task_out, "agent", "unknown")),
                "raw": raw,
                "parsed": parsed,
            })

    return outputs


def save_agent_output(result):
    output = {}
    output["final_raw"] = getattr(result, "raw", None)
    output["tasks"] = []

    if hasattr(result, "tasks_output"):
        for i, task_out in enumerate(result.tasks_output, start=1):
            task_data = {
                "task_index": i,
                "agent": str(getattr(task_out, "agent", "unknown")),
                "raw": getattr(task_out, "raw", None),
                "json_dict": getattr(task_out, "json_dict", None),
            }

            try:
                task_data["all_fields"] = make_json_safe(task_out.__dict__)
            except:
                task_data["all_fields"] = "Not accessible"

            output["tasks"].append(task_data)

    try:
        output["full_object"] = make_json_safe(result.__dict__)
    except:
        output["full_object"] = str(result)

    try:
        save_json(OUTPUT_AGENT_PATH, output)
    except Exception as e:
        print(f"Error saving file: {e}")

def fetch_master_rules(job_type):
    if job_type == DATA_QUALITY:
        return load_json(MASTER_DQ_RULES_PATH)
    else:
        return load_json(MASTER_DT_RULES_PATH)
    
def fetch_prompt(job_type):
    if job_type == DATA_QUALITY:
        return get_prompt(DQ_RULE_GENERATION_PROMPT)
    else:
        return get_prompt(DT_RULE_GENERATION_PROMPT)