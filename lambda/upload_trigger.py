import json
import boto3
import os
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    # Extract bucket and key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Generate a unique filename by appending date, time, and milliseconds
    base_name, extension = os.path.splitext(key)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")[:-3]
    unique_key = f"{base_name}_{timestamp}{extension}"

    logger.info("Starting Step Functions execution for bucket: %s, key: %s", bucket, unique_key)

    try:
        # Start the Step Functions execution with target languages
        response = stepfunctions.start_execution(
            stateMachineArn=os.environ['STATE_MACHINE_ARN'],
            input=json.dumps({
                'bucket': bucket,
                'key': unique_key,
                'target_languages': ['es', 'fr', 'de']
            })
        )

        logger.info("Started Step Functions execution: %s", response['executionArn'])

        return {
            'statusCode': 200,
            'body': json.dumps('Step Function execution started!')
        }
    except Exception as e:
        logger.error("Error starting Step Functions execution: %s", e)
        raise e
