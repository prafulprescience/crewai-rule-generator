"""crew.py: CrewAI Crew definition for rule generation workflow"""

__author__ = "Praful"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"

import json
from crewai import Crew, Process
from dotenv import load_dotenv
from helpers.config_reader import  load_incidents_bundle, load_yaml
from helpers.helpers import (
    _fill_ini_prompt_placeholders,
    extract_agent_output,
    save_agent_output,
    fetch_master_rules,
    fetch_prompt,
)
from constants import (
    DT_RULE_GENERATION_PROMPT,
    PAYLOAD_MAPPING_PROMPT,
    TASKS_CONFIG_PATH,
    load_json,
    safe_parse_json,
    save_json,
)
from agents.rule_agents import (
    create_data_quality_analyst_agent,
    create_rule_generator_agent,
)
from tasks.rule_generation_tasks import (
    create_analyze_dataset_task,
    create_generate_rules_task,
)

load_dotenv()


def create_rule_generation_crew(job_type, data_profile, additional_info):
    tasks_cfg = load_yaml(TASKS_CONFIG_PATH)
    data_quality_analyst = create_data_quality_analyst_agent()
    rule_generator = create_rule_generator_agent()

    master_rules = fetch_master_rules(job_type)
    rule_generation_prompt = fetch_prompt(job_type)
        
    rule_prompt_template = _fill_ini_prompt_placeholders(
        rule_generation_prompt,
        data_profile = json.dumps(data_profile, indent=2),
        additional_info = additional_info,
        master_rules=json.dumps(master_rules, indent=2)
    )

    # Task : Analyze the Dataset
    analyze_cfg = tasks_cfg["analyze_dataset"]
    analyze_dataset_task = create_analyze_dataset_task(
        agent=data_quality_analyst,
        task_config=analyze_cfg,
        placeholders={
            "ds_info": json.dumps(data_profile, indent=2),
            "additional_info": additional_info,
            "master_rules": json.dumps(master_rules, indent=2),
        },
    )

    # Task : Generate Rules
    gen_cfg = tasks_cfg["generate_rules"]
    generate_rules_task = create_generate_rules_task(
        agent=rule_generator,
        task_config=gen_cfg,
        rule_prompt_template=rule_prompt_template,
        context_tasks=[analyze_dataset_task],
    )

    crew = Crew(
        agents=[data_quality_analyst, rule_generator],
        tasks=[
            analyze_dataset_task,
            generate_rules_task,
        ],
        process=Process.sequential,
        verbose=False,
    )
    return crew


def run_agents(job_type, data_profile, additional_info):
    try:
        crew = create_rule_generation_crew(job_type, data_profile, additional_info)
        result = crew.kickoff()

        save_agent_output(result)
        res = extract_agent_output(result)

        return res[0], res[1]['parsed']

    except Exception as ex:
        raise Exception(f"Rule generation failed : {ex}")
