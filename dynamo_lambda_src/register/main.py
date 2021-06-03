import boto3

TABLE_NAME = 'Users'


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
    print(item_data)
    response = client.put_item(
        Item=item_data,
        ReturnConsumedCapacity='TOTAL',
        TableName=TABLE_NAME,
    )
    return 'ConsumedCapacity' in response and 'CapacityUnits' in response['ConsumedCapacity'] and \
           response['ConsumedCapacity']['CapacityUnits'] == 1


def lambda_handler(event, context):
    success = False
    if 'userId' not in event or 'password' not in event:
        print("Need userId or password")
    else:
        success = add_user(event)
    return {
        "success": success,
        "authToken": "token" if success else None
    }
