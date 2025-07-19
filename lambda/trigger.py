import json
import boto3
import os
import logging
from typing import Any, Dict

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda function handler to start a Step Functions execution based on S3 event.

    Args:
        event (Dict[str, Any]): The event data from S3.
        context (Any): The runtime information of the Lambda function.

    Returns:
        Dict[str, Any]: A response dictionary with status code and message.
    """
    logger.info("Received event: %s", json.dumps(event))

    # Extract bucket and key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    logger.info("Starting Step Functions execution for bucket: %s, key: %s", bucket, key)

    try:
        # Start the Step Functions execution
        response = stepfunctions.start_execution(
            stateMachineArn=os.environ['STATE_MACHINE_ARN'],
            input=json.dumps({
                'bucket': bucket,
                'key': key,
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
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error starting Step Function execution: {str(e)}')
        }
