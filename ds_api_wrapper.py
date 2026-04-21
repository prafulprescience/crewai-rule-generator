"""ds_api_wrapper.py: DataSentinel API wrapper methods"""

__author__ = "Praful"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"

import os
import requests
from dotenv import load_dotenv

load_dotenv()

DS_BASE_URL = os.getenv("DS_BASE_URL")
DS_TENANT_ID = os.getenv("DS_TENANT_ID")
DS_USERNAME = os.getenv("DS_USERNAME")
DS_PASSWORD = os.getenv("DS_PASSWORD")


def get_access_token() -> str:
    url = f"{DS_BASE_URL}/auth/token/"
    payload = {
        "credentials": {"user_name": DS_USERNAME, "user_pass": DS_PASSWORD, "remember": True}
    }

    headers = {"Content-Type": "application/json", "X-Tenant-ID": DS_TENANT_ID}

    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()["access_token"]


def get_dq_suite(token: str, suite_id: int) -> dict:
    url = f"{DS_BASE_URL}/dqsuites/{suite_id}"
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": DS_TENANT_ID}

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()


def get_dq_job_suite_id(token: str, job_id: int) -> int:
    url = f"{DS_BASE_URL}/jobs/{job_id}/dqsuite"
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": DS_TENANT_ID}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    data = r.json()
    return data["id"]


def get_dq_job_name(token: str, job_id: int) -> int:
    url = f"{DS_BASE_URL}/jobs/{job_id}"
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": DS_TENANT_ID}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    data = r.json()
    return data["name"]


def update_dq_suite(token: str, suit_id: int, payload: dict):
    url = f"{DS_BASE_URL}/dqsuites/{suit_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": DS_TENANT_ID,
    }

    r = requests.put(url, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()


def trigger_job(token: str, job_id: int):
    url = f"{DS_BASE_URL}/jobs/{job_id}/performAction"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": DS_TENANT_ID,
    }

    payload = {"action": "Run"}
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()


def update_job_review_status(token: str, job_id: int, ai_score: float, is_active: bool):
    url = f"{DS_BASE_URL}/jobs/{job_id}/updateReviewStatus"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": DS_TENANT_ID,
    }

    payload = None
    if is_active:
        payload = {
            "review_status": "Active",
            "reviewer_comments": "Rule suite is updated, no need for human review as AI score is 1.",
            "ai_score": ai_score
        }
    else:
        payload = {
            "review_status": "Review-Required",
            "reviewer_comments": "Rule suite is updated, needs human review.",
            "ai_score": ai_score
        }
    r = requests.put(url, headers=headers, json=payload)
    r.raise_for_status()


def get_dq_job_datasource_id(token: str, job_id: int) -> int:
    url = f"{DS_BASE_URL}/jobs/{job_id}"
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": DS_TENANT_ID}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    data = r.json()
    return data["datasource_id"]


def get_ds_info(token: str, ds_id: int) -> int:
    url = f"{DS_BASE_URL}/datasources/{ds_id}"
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": DS_TENANT_ID}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    data = r.json()
    return data["additional_info"]
