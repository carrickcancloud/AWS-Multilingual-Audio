import json
import boto3
import os
import logging
from botocore.exceptions import ClientError
from typing import Dict, Any

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
s3 = boto3.client('s3')
polly = boto3.client('polly')

# Define voice mapping for different languages
VOICE_MAPPING: Dict[str, str] = {
    'es': 'Lucia',    # Spanish voice
    'fr': 'Celine',   # French voice
    'de': 'Hans'      # German voice
}

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function to synthesize speech from translated texts using Amazon Polly.

    Args:
        event (Dict[str, Any]): Contains input parameters including bucket name,
                                 translated texts, and original filename.
        context (Any): Lambda context object.

    Returns:
        Dict[str, Any]: Response containing status code and results or error message.
    """
    logger.info("Synthesize function invoked")
    logger.info("Received event: %s", json.dumps(event))

    # Extract the necessary data from the event
    bucket: str = event.get('bucket')
    translated_texts: Dict[str, str] = event.get('translated_texts', {})
    original_filename: str = event.get('original_filename')

    results: Dict[str, str] = {}

    # Check if there are translations to synthesize
    if not translated_texts:
        logger.error("No translated texts provided for synthesis.")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No translations available'})
        }

    try:
        for target_language, translated_text in translated_texts.items():
            logger.info(f"Synthesizing speech for language: {target_language}")

            # Get the voice ID for the target language
            voice_id: str = VOICE_MAPPING.get(target_language, 'Joanna')
            logger.info(f"Using voice ID: {voice_id} for language: {target_language}")

            # Synthesize speech using Amazon Polly
            response: Dict[str, Any] = polly.synthesize_speech(
                Text=translated_text,
                OutputFormat='mp3',
                VoiceId=voice_id
            )

            # Define the URI for the audio output
            audio_uri: str = f's3://{bucket}/audio_outputs/{original_filename}_{target_language}.mp3'

            # Save the audio to S3
            s3.put_object(
                Bucket=bucket,
                Key=f'audio_outputs/{original_filename}_{target_language}.mp3',
                Body=response['AudioStream'].read()
            )

            logger.info(f"Synthesized speech saved to: {audio_uri}")
            results[target_language] = audio_uri

        return {
            'statusCode': 200,
            'body': json.dumps({'results': results})
        }

    except ClientError as e:
        logger.error(f"Client error synthesizing speech: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Client error occurred'})
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'An unexpected error occurred'})
        }
