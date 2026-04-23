"""app.py: DataSentinel AI agent code using CrewAI"""

__author__ = "Praful"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"

import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from constants import (
    DATA_QUALITY,
    DATA_TRANSFORMATION,
    OUTPUT_PAYLOAD_PATH,
    OUTPUT_RULES_PATH,
    save_json,
)
from crew import run_agents

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/generate-rules", methods=["POST"])
def generate_rules():
    try:
        logger.info("[/generate-rules] Request started")

        data = request.json
        if not data:
            raise Exception("No input data received.")

        data_profile = data.get("data_profile")
        additional_info = data.get("additional_info")
        job_type = data.get("type")

        if job_type not in [DATA_TRANSFORMATION, DATA_QUALITY]:
            raise Exception(
                "Invalid job type. Please specify either 'DataTransformation' or 'DataQuality'."
            )

        logger.info(f"[/generate-rules] Running agents with job_type: {job_type}")
        _, generated_rules, mapped_rules = run_agents(
            job_type, data_profile, additional_info
        )

        logger.info(f"[/generate-rules] Generated {len(mapped_rules)} rules")
        save_json(OUTPUT_RULES_PATH, generated_rules)
        save_json(OUTPUT_PAYLOAD_PATH, mapped_rules)

        logger.info("[/generate-rules] Completed successfully")
        return (
            jsonify(
                {
                    "status": "Success",
                    "message": "Rules generated and mapped successfully",
                    "data": mapped_rules,
                }
            ),
            200,
        )

    except Exception as ex:
        logger.error(f"[/generate-rules] Error: {str(ex)}")
        return jsonify({"status": "Error", "message": f"Error : {str(ex)}"}), 500


# Additional endpoints for testing connectivity
@app.route("/", methods=["GET"])
def home():
    return "Welcome to the DataSentinel AI Agent for Rule Generation!"


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5001
    app.run(host=host, port=port, debug=True)
