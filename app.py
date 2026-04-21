"""app.py: DataSentinel AI agent code using CrewAI"""

__author__ = "Praful"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from constants import (
    OUTPUT_PAYLOAD_PATH,
    OUTPUT_RULES_PATH,
    MASTER_RULES_PATH,
    save_json,
    load_json,
)
from crew import run_agents
from rule_selector import (
    validate_and_normalize_rules,
)
from ds_api_wrapper import (
    get_access_token,
    get_dq_job_suite_id,
    update_dq_suite,
    trigger_job,
    get_dq_suite,
    update_job_review_status,
    get_dq_job_datasource_id,
    get_ds_info,
    get_dq_job_name,
)

load_dotenv()

app = Flask(__name__)


@app.route('/connector/trigger', methods=['POST'])
def trigger_workflow():
    try:
        print("Entering trigger_workflow.")
        data = request.json
        if not data:
            raise Exception("No input data received.")

        job_id = data['job_id']
        incident_type = data.get('incident_type', None)

        token = get_access_token()
        job_name = get_dq_job_name(token, job_id)

        print(f"▶ Connecting DataSentinel server and generating token...Job name = {job_name}")
        if not token:
            raise Exception('Failed to connect to DataSentinel server. Please check the credentials.')

        ds_id = get_dq_job_datasource_id(token, job_id)
        ds_info = get_ds_info(token, ds_id)

        suite_id = get_dq_job_suite_id(token, job_id)
        existing_payload = get_dq_suite(token, suite_id)

        print("▶ Running agents to generate transformation rules...")
        analyze_incidents_task_res, generate_rules_task_res, map_to_payload_task_res, review_output_task_res = run_agents(incident_type, ds_info, existing_payload)

        save_json(OUTPUT_RULES_PATH, generate_rules_task_res['parsed'])
        save_json(OUTPUT_PAYLOAD_PATH, map_to_payload_task_res['parsed'])
        print("▶ Saving updated payload & selected rules locally...")

        # print("▶ Updating DQ Suite via PUT...")
        # update_dq_suite(token, suite_id, map_to_payload_task_res['parsed'])

        print("✅ Workflow completed successfully!")
        return jsonify({"status": "Success", "message": ""})
    
    except Exception as ex:
        raise Exception(f"Error in executing trigger_workflow : {ex}")
    
    finally:
        print("Exiting trigger_workflow.")


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    app.run(host=host, port=port, debug=True)
