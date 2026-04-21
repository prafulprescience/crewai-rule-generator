"""crew.py: CrewAI Crew definition for rule generation workflow"""

__author__ = "Praful"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"

import json
from typing import Optional

from crewai import Crew, Task, Process
from dotenv import load_dotenv
from config_reader import get_prompt, load_incidents_bundle, load_yaml
from constants import (
    DT_RULE_GENERATION_PROMPT,
    VALIDIO_DT_RULE_GENERATION_PROMPT,
    PAYLOAD_MAPPING_PROMPT,
    MASTER_RULES_PATH,
    OUTPUT_AGENT_PATH,
    TASKS_CONFIG_PATH,
    VALIDIO,
    load_json,
    safe_parse_json,
    save_json,
)
from agents.rule_agents import (
    create_incident_analyst_agent,
    create_rule_generator_agent,
    create_payload_mapper_agent,
    create_quality_reviewer_agent,
)

load_dotenv()


def _apply_task_placeholders(template: str, replacements: dict[str, str]) -> str:
    out = template
    for key, value in replacements.items():
        out = out.replace(f"<<{key.upper()}>>", value)
    return out


def _fill_ini_prompt_placeholders(
    template: str,
    *,
    incident_json: Optional[str] = None,
    master_rules: Optional[str] = None,
    ds_info: Optional[str] = None,
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


def create_rule_generation_crew(incident_type, ds_info, existing_payload):
    tasks_cfg = load_yaml(TASKS_CONFIG_PATH)
    incident_analyst = create_incident_analyst_agent()
    rule_generator = create_rule_generator_agent()
    payload_mapper = create_payload_mapper_agent()
    quality_reviewer = create_quality_reviewer_agent()

    master_rules = load_json(MASTER_RULES_PATH)
    payload_mapping_prompt = get_prompt(PAYLOAD_MAPPING_PROMPT)
    incidents_bundle = load_incidents_bundle(incident_type)

    if incident_type == VALIDIO:
        rule_prompt_raw = get_prompt(VALIDIO_DT_RULE_GENERATION_PROMPT)
    else:
        rule_prompt_raw = get_prompt(DT_RULE_GENERATION_PROMPT)

        
    rule_prompt_template = _fill_ini_prompt_placeholders(
        rule_prompt_raw,
        incident_json=json.dumps(incidents_bundle, indent=2),
        master_rules=json.dumps(master_rules, indent=2),
        ds_info=json.dumps(ds_info, indent=2),
    )

    payload_prompt_filled = _fill_ini_prompt_placeholders(
        payload_mapping_prompt,
        master_rules=json.dumps(master_rules, indent=2),
        generated_rule=(
            "Use the intent-level rules JSON from the previous generate_rules task output in this crew."
        ),
        existing_payload=json.dumps(existing_payload, indent=2),
    )

    # Task : Analyze the incident
    analyze_cfg = tasks_cfg["analyze_incidents"]
    analyze_incidents_task = Task(
        description=_apply_task_placeholders(
            analyze_cfg["description"],
            {
                "INCIDENT_TYPE": incident_type or "general",
                "DS_INFO": json.dumps(ds_info, indent=2),
                "INCIDENTS_JSON": json.dumps(incidents_bundle, indent=2),
                "MASTER_RULES": json.dumps(master_rules, indent=2),
            },
        ),
        expected_output=analyze_cfg["expected_output"].strip(),
        agent=incident_analyst,
    )

    # Task : Generate Rules
    gen_cfg = tasks_cfg["generate_rules"]
    generate_rules_task = Task(
        description=_apply_task_placeholders(
            gen_cfg["description"],
            {"RULE_PROMPT_TEMPLATE": rule_prompt_template},
        ),
        expected_output=gen_cfg["expected_output"].strip(),
        agent=rule_generator,
        context=[analyze_incidents_task],
    )

    # Task : Map rules with payload
    map_cfg = tasks_cfg["map_to_payload"]
    map_to_payload_task = Task(
        description=_apply_task_placeholders(
            map_cfg["description"],
            {
                "payload_mapping_prompt": payload_prompt_filled,
                "EXISTING_PAYLOAD": json.dumps(existing_payload, indent=2),
            },
        ),
        expected_output=map_cfg["expected_output"].strip(),
        agent=payload_mapper,
        context=[generate_rules_task],
    )

    # Task : Review the results generated
    review_cfg = tasks_cfg["review_output"]
    review_output_task = Task(
        description=review_cfg["description"].strip(),
        expected_output=review_cfg["expected_output"].strip(),
        agent=quality_reviewer,
        context=[map_to_payload_task, generate_rules_task],
    )

    crew = Crew(
        agents=[incident_analyst, rule_generator, payload_mapper, quality_reviewer],
        tasks=[
            analyze_incidents_task,
            generate_rules_task,
            map_to_payload_task,
            review_output_task,
        ],
        process=Process.sequential,
        verbose=False,
    )

    return crew


def run_agents(incident_type, ds_info, existing_payload):
    try:
        crew = create_rule_generation_crew(incident_type, ds_info, existing_payload)
        result = crew.kickoff()

        save_agent_output(result)
        res = extract_agent_output(result)

        return res[0], res[1], res[2], res[3]

    except Exception as ex:
        raise Exception(f"Rule generation failed : {ex}")
