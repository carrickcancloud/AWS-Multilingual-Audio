import boto3
import logging
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')

def lambda_handler(event, context):
    logger.info("Transcribe function invoked")
    bucket = event['bucket']
    key = event['key']
    job_name = key.split('.')[0]

    try:
        logger.info(f"Starting transcription job: {job_name}")
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{bucket}/{key}'},
            MediaFormat='mp3',
            LanguageCode='en-US'
        )

        transcript_uri = f's3://{bucket}/transcripts/{job_name}.txt'
        logger.info(f"Transcription job started: {transcript_uri}")
        return {'transcript_uri': transcript_uri}

    except ClientError as e:
        logger.error(f"Error starting transcription job: {e}")
        raise e
