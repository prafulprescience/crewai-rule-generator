"""rule_agents.py: CrewAI Agents for data quality rule generation"""

__author__ = "Praful"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"

import os

from crewai import Agent, LLM
from helpers.config_reader import load_yaml
from dotenv import load_dotenv
from constants import (
    AGENTS_CONFIG_PATH,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_MODEL,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPEN_AI_DEFAULT_MODEL_NAME,
    AZURE_OPEN_AI_DEFAULT_VERSION,
)

load_dotenv()


def load_agents_config() -> dict:
    return load_yaml(AGENTS_CONFIG_PATH)


def get_azure_llm() -> LLM:
    deployment = os.getenv(AZURE_OPENAI_MODEL, AZURE_OPEN_AI_DEFAULT_MODEL_NAME)
    endpoint = (os.getenv(AZURE_OPENAI_ENDPOINT))
    return LLM(
        model=f"azure/{deployment}",
        is_litellm=True,
        provider="litellm",
        api_key=os.getenv(AZURE_OPENAI_API_KEY),
        api_base=endpoint,
        api_version=os.getenv(AZURE_OPENAI_API_VERSION, AZURE_OPEN_AI_DEFAULT_VERSION),
        temperature=0,
    )


def create_data_quality_analyst_agent() -> Agent:
    config = load_agents_config()["data_quality_analyst"]
    
    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        verbose=False,
        allow_delegation=False,
        llm=get_azure_llm(),
    )

def data_profile_analyst_agent() -> Agent:
    config = load_agents_config()["data_profile_analyst"]
    
    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        verbose=False,
        allow_delegation=False,
        llm=get_azure_llm(),
    )

def create_rule_generator_agent() -> Agent:
    config = load_agents_config()["rule_generator"]
    
    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        verbose=False,
        allow_delegation=False,
        llm=get_azure_llm()
    )


def create_payload_mapper_agent() -> Agent:
    config = load_agents_config()["payload_mapper"]
    
    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        verbose=False,
        allow_delegation=False,
        llm=get_azure_llm(),
    )


def create_quality_reviewer_agent() -> Agent:
    config = load_agents_config()["quality_reviewer"]
    
    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        verbose=False,
        allow_delegation=True,
        llm=get_azure_llm()
    )
