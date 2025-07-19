import json
import boto3
import logging
import time
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')

def lambda_handler(event, context):
    logger.info("Transcribe function invoked")

    # Extract bucket and key from the event
    bucket = event['bucket']
    key = event['key']

    # Ensure a unique transcription job name
    job_name = f"{key.split('.')[0]}-{int(time.time())}"  # Append timestamp for uniqueness

    try:
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
            logger.error(f"Transcription job failed: {response['TranscriptionJob']['FailureReason']}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Transcription job failed'})
            }

    except ClientError as e:
        logger.error(f"Error starting transcription job: {e}")
        raise e
