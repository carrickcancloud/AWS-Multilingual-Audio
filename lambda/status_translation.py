import json
import boto3
import logging
from botocore.exceptions import ClientError
from typing import Dict, Any

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
translate = boto3.client('translate')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function to check the status of a translation job.

    Parameters:
    event (Dict[str, Any]): The input event containing the translation job ID.
    context (Any): The context object provided by AWS Lambda.

    Returns:
    Dict[str, Any]: A dictionary containing the status of the translation job.
    """
    logger.info("Check Translation Status function invoked")
    logger.info("Received event: %s", json.dumps(event))

    # Extract job ID from the event
    translation_job_id = event.get('translation_job_id')

    if not translation_job_id:
        logger.error("Translation job ID is missing from the event.")
        return {'status': 'ERROR', 'message': 'Translation job ID is required.'}

    try:
        logger.info(f"Checking status of translation job: {translation_job_id}")

        # Check the status of the translation job
        response = translate.get_translation_job(TranslationJobName=translation_job_id)

        # Extract job status from the response
        job_status = response['TranslationJob']['JobStatus']
        logger.info(f"Translation job status: {job_status}")

        return {
            'status': job_status,
        }

    except ClientError as e:
        logger.error(f"Error checking translation job: {e}")
        return {'status': 'ERROR', 'message': str(e)}
