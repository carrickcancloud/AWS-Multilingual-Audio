import json
import boto3
import logging
from botocore.exceptions import ClientError
from typing import Any, Dict

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
polly = boto3.client('polly')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, str]:
    """
    Lambda function to check the status of a Polly synthesis job.

    Args:
        event (Dict[str, Any]): The event data containing the synthesis job ID.
        context (Any): The context object provided by AWS Lambda.

    Returns:
        Dict[str, str]: A dictionary containing the status of the synthesis job.
    """
    logger.info("Check Synthesis Status function invoked")
    logger.info("Received event: %s", json.dumps(event))

    # Extract job ID from the event
    synthesis_job_id = event.get('synthesis_job_id')

    if not synthesis_job_id:
        logger.error("No synthesis job ID provided in the event.")
        return {
            'status': 'ERROR',
            'message': 'No synthesis job ID provided.'
        }

    try:
        logger.info(f"Checking status of synthesis job: {synthesis_job_id}")

        # Check the status of the synthesis job
        response = polly.get_synthesis_job(JobName=synthesis_job_id)

        # Extract job status from the response
        job_status = response['SynthesisJob']['Status']
        logger.info(f"Synthesis job status: {job_status}")

        return {
            'status': job_status,
        }

    except ClientError as e:
        logger.error(f"Error checking synthesis job: {e}")
        return {
            'status': 'ERROR',
            'message': str(e)
        }
