import boto3

TABLE_NAME = 'Users'


def lambda_handler(event, context):
    client = boto3.client('dynamodb')
    user_id = event['userId']
    password = event['password']
    response = client.query(
        ExpressionAttributeValues={
            ':u': {
                'S': user_id,
            },
            ":h": {
                'N': "-1"
            }
        },
        KeyConditionExpression='userId = :u AND roomId = :h',
        ProjectionExpression='password',
        TableName=TABLE_NAME,
    )
    resp = response['Items']
    success = False
    if len(resp) == 1:
        pswd = resp[0]['password']['S']
        success = pswd == password
    else:
        print("We had a problem finding the user")
    return {
        "success": success,
        "authToken": "token" if success else None
    }
