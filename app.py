"""app.py: DataSentinel AI agent code using CrewAI"""

__author__ = "Praful"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"

import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from constants import (
    DATA_QUALITY,
    DATA_TRANSFORMATION,
    OUTPUT_PAYLOAD_PATH,
    OUTPUT_RULES_PATH,
    AI_THRESHOLD_CONFIDENCE,
    save_json,
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)


#function to 
@app.route('/generate-rules', methods=['POST'])
def generate_rules():
    try:
        logger.info("[/generate-rules] Request started")
        
        data = request.json
        if not data:
            raise Exception("No input data received.")

        data_profile = data.get('data_profile')
        additional_info = data.get('additional_info')
        job_type  =  data.get("type")

        if job_type not in [DATA_TRANSFORMATION, DATA_QUALITY]:
            raise Exception("Invalid job type. Please specify either 'DataTransformation' or 'DataQuality'.")
        
        logger.info(f"[/generate-rules] Running agents with job_type: {job_type}")
        _, generated_rules, mapped_rules = run_agents(job_type, data_profile, additional_info)

        logger.info(f"[/generate-rules] Generated {len(mapped_rules)} rules")
        save_json(OUTPUT_RULES_PATH, generated_rules)
        save_json(OUTPUT_PAYLOAD_PATH, mapped_rules)

        logger.info("[/generate-rules] Completed successfully")
        return jsonify({
            "status": "Success",
            "message": "Rules generated and mapped successfully",
            "data": mapped_rules
        }), 200

    except Exception as ex:
        logger.error(f"[/generate-rules] Error: {str(ex)}")
        return jsonify({
            "status": "Error",
            "message": f"Error : {str(ex)}"
        }), 500




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

        print("▶ Updating DQ Suite via PUT...")
        #update_dq_suite(token, suite_id, map_to_payload_task_res['parsed'])

        # Check confidence and trigger job based on AI_THRESHOLD_CONFIDENCE and auto-trigger flag
        review_data = review_output_task_res.get('parsed', {})
        ai_confidence_score = review_data.get('average_confidence', 0)
        auto_trigger = os.getenv("AUTO_TRIGGER_ON_FULL_SCORE", "false").lower() == "true"
        
        if ai_confidence_score >= AI_THRESHOLD_CONFIDENCE:
            if auto_trigger:
                print(f"▶ AI confidence score is {ai_confidence_score} & auto-trigger enabled. Triggering job...")
                #update_job_review_status(token, job_id, ai_confidence_score, True)
                #trigger_job(token, job_id)
            else:
                print(f"▶ AI confidence score is {ai_confidence_score} but auto-trigger disabled. Skipping trigger.")
                #update_job_review_status(token, job_id, ai_confidence_score, False)
        else:
            print("▶ AI confidence score below threshold. Updating job review status...")
            #update_job_review_status(token, job_id, ai_confidence_score, False)

        print("✅ Workflow completed successfully!")
        return jsonify({"status": "Success", "message": ""})
    
    except Exception as ex:
        return jsonify({
            "status": "Error",
            "message": f"Error in trigger_workflow: {str(ex)}"
        }), 500
    
    finally:
        print("Exiting trigger_workflow.")

# Additional endpoints for testing connectivity
@app.route('/', methods=['GET'])
def home():
    return "Welcome to the DataSentinel AI Agent for Rule Generation!"


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5001
    app.run(host=host, port=port, debug=True)
