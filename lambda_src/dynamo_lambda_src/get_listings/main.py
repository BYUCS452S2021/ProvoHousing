import boto3

TABLE_NAME = 'foo'

def lambda_handler(event, context):
    client = boto3.client('dynamodb')
    return {
        "hello": "world"
    }