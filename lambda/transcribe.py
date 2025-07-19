import json
import boto3
import logging
import time
from botocore.exceptions import ClientError
from datetime import datetime
from typing import Dict, Any

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda function to handle audio transcription using Amazon Transcribe.

    Args:
        event (Dict[str, Any]): The event data containing the S3 bucket and key.
        context (Any): The context object provided by AWS Lambda.

    Returns:
        Dict[str, Any]: A response object containing the status code and body.
    """
    logger.info("Transcribe function invoked")
    logger.info("Received event: %s", json.dumps(event))

    # Extract bucket and key from the event
    bucket = event['bucket']
    key = event['key']

    logger.info(f"Checking existence of object in bucket: {bucket}, key: {key}")

    # Ensure a unique transcription job name using only the base filename
    base_name = key.split('/')[-1].split('.')[0]
    job_name = f"{base_name}-{int(time.time())}"

    try:
        # Check if the S3 object exists
        s3.head_object(Bucket=bucket, Key=key)
        logger.info(f"Object exists: s3://{bucket}/{key}")

        logger.info(f"Starting transcription job: {job_name}")

        # Start the transcription job
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{bucket}/{key}'},
            MediaFormat='mp3',
            LanguageCode='en-US'
        )

        # Poll for job completion
        while True:
            logger.info(f"Checking status of transcription job: {job_name}")
            response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job_status = response['TranscriptionJob']['TranscriptionJobStatus']

            if job_status in ['COMPLETED', 'FAILED']:
                break

            logger.info(f"Transcription job status: {job_status}")
            time.sleep(5)

        if job_status == 'COMPLETED':
            transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
            logger.info(f"Transcription job completed: {transcript_uri}")
            return {
                'statusCode': 200,
                'body': json.dumps({'transcript_uri': transcript_uri})
            }
        else:
            failure_reason = response['TranscriptionJob'].get('FailureReason', 'Unknown error')
            logger.error(f"Transcription job failed: {failure_reason}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Transcription job failed', 'reason': failure_reason})
            }

    except ClientError as e:
        logger.error(f"Error checking object existence: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'S3 ClientError', 'message': str(e)})
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'message': str(e)})
        }
