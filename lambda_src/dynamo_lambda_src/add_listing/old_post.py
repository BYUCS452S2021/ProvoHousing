import boto3
from random import randint

TABLE_NAME = 'Housing'


def get_next_room_id():
    client = boto3.client('dynamodb')
    resp = client.get_item(
        TableName=TABLE_NAME,
        Key={
            'userId': {
                'S': 'count'
            },
            'roomId': {
                'N': '-1'
            }
        },
        AttributesToGet=['totalRoomCount'],
    )
    return resp['Item']['totalRoomCount']['N'] + 1


def post_housing(event):
    client = boto3.client('dynamodb')

    # Generate roomId
    roomId = get_next_room_id()
    print("This is the random RoomId:", roomId)

    # Get userId
    if 'userId' in event.keys():
        print("This is the userId")
        userId = event['userId']
        print(userId)
    else:
        print("userId not found.")
        userId = ''

    # Get address
    if 'addressFull' in event.keys():
        print("This is the address:")
        address = event['addressFull']
        print(address)
    else:
        print("address not found.")
        address = None

    # Get price
    if 'pricePerMonth' in event.keys():
        print("This is the price per month:")
        price = event['pricePerMonth']
        print(price)
    else:
        print("pricePerMonth not found")
        price = None

    # Get endContract
    if 'endContract' in event.keys():
        print("This is the end of contract:")
        endContract = event['endContract']
        print(endContract)
    else:
        print("endContract not found.")
        endContract = None

    # Get washer_dryer
    if 'hasWasher' in event.keys():
        print("This is the washer_dryer value:")
        washer_dryer = event['hasWasher']
        print(washer_dryer)
    else:
        print("hasWasher not found.")
        washer_dryer = None

    # Get dishwasher
    if 'hasDishwasher' in event.keys():
        print("This is the dishwasher value:")
        dishwasher = event['hasDishwasher']
        print(dishwasher)
    else:
        print("hasDishwasher not found")
        dishwasher = None

    # Determine if Single or Married
    if 'isMarried' in event.keys():
        print("This is the isMarried value:")
        isMarried = event['isMarried']
        print(isMarried)
    else:
        print("isMarried not found")
        isMarried = None

    if isMarried:
        # Married housing
        item_data = {
            'roomId': {
                'N': str(roomId),
            },
            'userId': {
                'S': userId,
            },
        }

    else:
        # Single housing
        item_data = {
            'roomId': {
                'N': str(roomId),
            },
            'userId': {
                'S': userId,
            },
        }

    client.put_item(
        Item=item_data,
        TableName=TABLE_NAME
    )

    return "success placeholder"


def lambda_handler(event, context):
    success = False
    success = post_housing(event)
    return success