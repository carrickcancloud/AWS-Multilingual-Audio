import json
import boto3
import os
import logging
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
translate = boto3.client('translate')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    logger.info("Translate function invoked")

    # Extract the necessary data from the event
    transcript_uri = event['transcript_uri']
    target_languages = event['target_languages']  # Expecting a list of languages
    bucket = event['bucket']
    key = event['key']

    results = {}

    try:
        logger.info(f"Retrieving transcript text from {transcript_uri}")

        # Retrieve the transcript text from S3
        transcript_object = s3.get_object(Bucket=bucket, Key=transcript_uri)
        transcript_text = transcript_object['Body'].read().decode('utf-8')  # Read and decode the transcript

        for target_language in target_languages:
            logger.info(f"Translating text to {target_language}")
            translated_text = translate.translate_text(Text=transcript_text, TargetLanguageCode=target_language)

            # Define the URI for the translation output with a clear naming convention
            original_filename = os.path.splitext(os.path.basename(key))[0]  # Get the base name without extension
            translation_uri = f's3://{bucket}/translations/{original_filename}_{target_language}.txt'

            # Save the translated text to S3
            s3.put_object(Bucket=bucket, Key=f'translations/{original_filename}_{target_language}.txt',
                          Body=translated_text['TranslatedText'])

            logger.info(f"Translation successful for {target_language}: {translation_uri}")
            results[target_language] = translation_uri  # Store the result for each language

        return {
            'statusCode': 200,
            'body': json.dumps({'results': results})  # Return all translation URIs
        }

    except ClientError as e:
        logger.error(f"Error translating text: {e}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise e
