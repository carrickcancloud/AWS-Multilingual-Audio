import json
import boto3
import logging
from botocore.exceptions import ClientError
from typing import Any, Dict, List

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
translate = boto3.client('translate')
s3 = boto3.client('s3')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda function to translate text retrieved from an S3 bucket.

    Args:
        event (Dict[str, Any]): Contains information about the S3 object and target languages.
        context (Any): AWS Lambda context object.

    Returns:
        Dict[str, Any]: Response containing the status code and results of translations.
    """
    logger.info("Translate function invoked")
    logger.info("Received event: %s", json.dumps(event))

    # Extract the necessary data from the event
    transcript_uri: str = event['transcript_uri']
    target_languages: List[str] = event['target_languages']
    bucket: str = event['bucket']
    original_filename: str = event['original_filename']

    results: Dict[str, str] = {}

    try:
        logger.info(f"Retrieving transcript text from {transcript_uri}")

        # Retrieve the transcript text from S3
        transcript_object = s3.get_object(Bucket=bucket, Key=transcript_uri)
        transcript_text: str = transcript_object['Body'].read().decode('utf-8')

        for target_language in target_languages:
            logger.info(f"Translating text to {target_language}")
            translated_text = translate.translate_text(Text=transcript_text, TargetLanguageCode=target_language)

            # Define the URI for the translation output with a clear naming convention
            translation_key: str = f'translations/{original_filename}_transcription_{target_language}.txt'

            # Save the translated text to S3
            s3.put_object(Bucket=bucket, Key=translation_key, Body=translated_text['TranslatedText'])

            logger.info(f"Translation successful for {target_language}: s3://{bucket}/{translation_key}")
            results[target_language] = f's3://{bucket}/{translation_key}'

        return {
            'statusCode': 200,
            'body': json.dumps({'results': results})
        }

    except ClientError as e:
        logger.error(f"Error retrieving transcript or translating text: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'An unexpected error occurred'})
        }
