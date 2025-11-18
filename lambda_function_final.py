"""
AWS Lambda Function for S3 to DynamoDB Integration
This function automatically records S3 object metadata to DynamoDB
Triggered by: S3 PutObject and DeleteObject events
"""

import json
import boto3
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb_resource = boto3.resource('dynamodb')

# Configuration
DYNAMODB_TABLE_NAME = 'awscapstoneDynamo'

def lambda_handler(event, context):
    """
    Main Lambda handler function
    Processes S3 events and updates DynamoDB
    
    Args:
        event: S3 event trigger
        context: Lambda context
        
    Returns:
        dict: Response with status code and message
    """
    
    try:
        print("Event received:", json.dumps(event))
        
        # Get DynamoDB table reference
        table = dynamodb_resource.Table(DYNAMODB_TABLE_NAME)
        
        # Process each S3 record
        for record in event['Records']:
            # Extract S3 event details
            bucket_name = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']
            object_size = record['s3']['object'].get('size', 0)
            event_name = record['eventName']
            event_time = record['eventTime']
            
            # Determine event type
            if 'ObjectCreated' in event_name:
                event_type = 'CREATED'
                operation = 'PUT'
            elif 'ObjectRemoved' in event_name:
                event_type = 'DELETED'
                operation = 'DELETE'
            else:
                event_type = 'UNKNOWN'
                operation = 'OTHER'
            
            # Extract filename from S3 path
            filename = object_key.split('/')[-1]
            
            # Get object metadata from S3
            try:
                response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
                content_type = response.get('ContentType', 'unknown')
            except Exception as e:
                print(f"Error getting object metadata: {e}")
                content_type = 'unknown'
            
            # Prepare DynamoDB item
            item = {
                'id': filename,  # Primary key
                'bucket': bucket_name,
                'key': object_key,
                'event_type': event_type,
                'timestamp': event_time,
                'size': object_size,
                'content_type': content_type,
                'operation': operation,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Write to DynamoDB
            print(f"Writing to DynamoDB: {item}")
            table.put_item(Item=item)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully processed S3 events and updated DynamoDB')
        }
    
    except Exception as e:
        print(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing event: {str(e)}')
        }
