import boto3
import os
import logging
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
polly = boto3.client('polly')


def lambda_handler(event, context):
    translated_text = event['translated_text']
    bucket = event['bucket']
    target_language = os.environ['TARGET_LANGUAGE']

    try:
        logger.info(f"Synthesizing speech for language: {target_language}")
        response = polly.synthesize_speech(Text=translated_text, OutputFormat='mp3', VoiceId='Joanna')

        audio_uri = f's3://{bucket}/audio_outputs/{event["key"].split(".")[0]}_{target_language}.mp3'

        # Save audio to S3
        s3.put_object(Bucket=bucket, Key=audio_uri, Body=response['AudioStream'].read())
        logger.info(f"Synthesized speech saved to: {audio_uri}")

        return {'audio_uri': audio_uri}

    except ClientError as e:
        logger.error(f"Error synthesizing speech: {e}")
        raise e
