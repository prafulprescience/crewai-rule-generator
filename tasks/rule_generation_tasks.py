"""tasks.py: CrewAI Task definitions for rule generation workflow"""

__author__ = "Praful"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"

from crewai import Task
from typing import Optional


def _apply_task_placeholders(template: str, replacements: dict[str, str]) -> str:
    """Apply placeholder replacements to task description template."""
    out = template
    for key, value in replacements.items():
        out = out.replace(f"<<{key.upper()}>>", value)
    return out


def create_analyze_dataset_task(
    agent,
    task_config: dict,
    placeholders: dict[str, str]
) -> Task:
    """
    Create the analyze dataset task with runtime-updated description.
    
    Args:
        agent: The dataset analyst agent
        task_config: Task configuration from tasks.yaml
        placeholders: Dictionary with keys like INCIDENT_TYPE, DS_INFO, etc.
    
    Returns:
        Task: Configured analyze dataset task
    """
    description = _apply_task_placeholders(
        task_config["description"],
        placeholders
    )
    
    return Task(
        description=description,
        expected_output=task_config["expected_output"].strip(),
        agent=agent,
    )


def create_generate_rules_task(
    agent,
    task_config: dict,
    rule_prompt_template: str,
    context_tasks: Optional[list] = None
) -> Task:
    """
    Create the generate rules task with runtime-updated description.
    
    Args:
        agent: The rule generator agent
        task_config: Task configuration from tasks.yaml
        rule_prompt_template: The filled rule prompt template
        context_tasks: List of context tasks (typically analyze_incidents_task)
    
    Returns:
        Task: Configured generate rules task
    """
    placeholders = {
        "RULE_PROMPT_TEMPLATE": rule_prompt_template
    }
    
    description = _apply_task_placeholders(
        task_config["description"],
        placeholders
    )
    
    context = context_tasks or []
    
    return Task(
        description=description,
        expected_output=task_config["expected_output"].strip(),
        agent=agent,
        context=context,
    )


def create_map_to_payload_task(
    agent,
    task_config: dict,
    master_rules: str,
    context_tasks: Optional[list] = None
) -> Task:
    """
    Create the map to payload task to transform generated rules into complete master rule format.
    
    Args:
        agent: The rule mapper agent
        task_config: Task configuration from tasks.yaml
        master_rules: JSON string of master rules catalog (for reference)
        context_tasks: List of context tasks (typically generate_rules_task)
    
    Returns:
        Task: Configured map to payload task
    """
    placeholders = {
        "MASTER_RULES": master_rules,
    }
    
    description = _apply_task_placeholders(
        task_config["description"],
        placeholders
    )
    
    context = context_tasks or []
    
    return Task(
        description=description,
        expected_output=task_config["expected_output"].strip(),
        agent=agent,
        context=context,
    )


def create_review_output_task(
    agent,
    task_config: dict,
    context_tasks: Optional[list] = None
) -> Task:
    """
    Create the review output task.
    
    Args:
        agent: The quality reviewer agent
        task_config: Task configuration from tasks.yaml
        context_tasks: List of context tasks
    
    Returns:
        Task: Configured review output task
    """
    context = context_tasks or []
    
    return Task(
        description=task_config["description"].strip(),
        expected_output=task_config["expected_output"].strip(),
        agent=agent,
        context=context,
    )
