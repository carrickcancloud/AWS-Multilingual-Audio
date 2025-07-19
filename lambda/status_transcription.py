import json
import boto3
import logging
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
transcribe = boto3.client('transcribe')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Optional[str]]:
    """
    Lambda function to check the status of a transcription job.

    Args:
        event (Dict[str, Any]): The event data containing 'job_name'.
        context (Any): The runtime information of the Lambda function.

    Returns:
        Dict[str, Optional[str]]: A dictionary containing the job status and transcript URI if completed.
    """
    logger.info("Check Transcription Status function invoked")
    logger.info("Received event: %s", json.dumps(event))

    # Extract job name from the event
    job_name = event.get('job_name')

    if not job_name:
        logger.error("No job name provided in the event.")
        return {'status': 'ERROR', 'message': 'Job name is required.'}

    try:
        logger.info(f"Checking status of transcription job: {job_name}")

        # Check the status of the transcription job
        response = transcribe.get_transcription_job(TranscriptionJobName=job_name)

        # Extract job status from the response
        job_status = response['TranscriptionJob']['TranscriptionJobStatus']
        logger.info(f"Transcription job status: {job_status}")

        return {
            'status': job_status,
            'transcript_uri': response['TranscriptionJob']['Transcript']['TranscriptFileUri'] if job_status == 'COMPLETED' else None
        }

    except ClientError as e:
        logger.error(f"Error checking transcription job: {e}")
        return {'status': 'ERROR', 'message': str(e)}

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {'status': 'ERROR', 'message': 'An unexpected error occurred.'}
