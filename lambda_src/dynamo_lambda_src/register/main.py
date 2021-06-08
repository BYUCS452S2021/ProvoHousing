import boto3

TABLE_NAME = 'Users'


def user_exists(user_id):
    client = boto3.client('dynamodb')
    resp = client.get_item(
        TableName = TABLE_NAME,
        Key = {
            'userId': {
                'S': user_id
            },
            'roomId': {
                'N': '-1'
            }
        }
    )
    return 'Item' in resp and len(resp['Item']) > 0


def add_user(event):
    client = boto3.client('dynamodb')
    item_data = {
        'roomId': {
            'N': '-1',
        },
    }
    for k, v in event.items():
        if type(k) != str or type(v) != str:
            print(f"Not including {k} because it is not a string")
            continue
        item_data[k] = {
            'S': v
        }
    response = client.put_item(
        Item=item_data,
        ReturnConsumedCapacity='TOTAL',
        TableName=TABLE_NAME,
    )
    return 'ConsumedCapacity' in response and 'CapacityUnits' in response['ConsumedCapacity'] and \
           response['ConsumedCapacity']['CapacityUnits'] == 1

def update_count():
    client = boto3.client('dynamodb')
    client.update_item(
        Key={
            'userId': {
                'S': 'count',
            },
            'roomId': {
                'N': '-1'
            }
        },
        TableName=TABLE_NAME,
        ExpressionAttributeValues={":inc": {'N': "1"}},
        UpdateExpression= "ADD numUsers :inc"
    )


def lambda_handler(event, context):
    success = False
    reason = ''
    if 'userId' not in event or 'password' not in event:
        reason = "Need userId or password"
    else:
        user_id = event['userId']
        if not user_exists(user_id):
            success = add_user(event)
            if success:
                update_count()
        else:
            reason = "User already exists"
    return {
        "success": success,
        "authToken": "token" if success else None,
        "reason": reason
    }


if __name__ == '__main__':
    e = {
        'userId': "testUser4",
        "password": "test123"
    }
    print(lambda_handler(e, None))