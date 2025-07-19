import json
import boto3
import os
import logging
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
s3 = boto3.client('s3')
polly = boto3.client('polly')

# Define voice mapping for different languages
VOICE_MAPPING = {
    'es': 'Lucia',    # Spanish voice
    'fr': 'Celine',   # French voice
    'de': 'Hans'      # German voice
}

def lambda_handler(event, context):
    logger.info("Synthesize function invoked")

    # Extract the necessary data from the event
    bucket = event['bucket']
    translated_texts = event['translated_texts']
    original_filename = event['original_filename']

    results = {}

    try:
        for target_language, translated_text in translated_texts.items():
            logger.info(f"Synthesizing speech for language: {target_language}")

            # Get the voice ID for the target language
            voice_id = VOICE_MAPPING.get(target_language, 'Joanna')

            # Synthesize speech using Amazon Polly
            response = polly.synthesize_speech(
                Text=translated_text,
                OutputFormat='mp3',
                VoiceId=voice_id
            )

            # Define the URI for the audio output
            audio_uri = f's3://{bucket}/audio_outputs/{original_filename}_{target_language}.mp3'

            # Save the audio to S3
            s3.put_object(Bucket=bucket, Key=f'audio_outputs/{original_filename}_{target_language}.mp3',
                          Body=response['AudioStream'].read())

            logger.info(f"Synthesized speech saved to: {audio_uri}")
            results[target_language] = audio_uri

        return {
            'statusCode': 200,
            'body': json.dumps({'results': results})
        }

    except ClientError as e:
        logger.error(f"Error synthesizing speech: {e}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise e
