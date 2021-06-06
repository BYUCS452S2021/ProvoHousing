import boto3

HOUSING_TABLE = 'Housing'
FILTER_TABLE = 'FilterHousing'

married_keys = ["married -- numBedrooms"]

single_keys = [
    "single -- male:single",
    "single -- male:shared",
    "single -- female:single",
    "single -- female:shared"
]

married_key_cols = ["numBedrooms"]

single_key_cols = ["isMale", "isShared"]

housing_cols = {
    'roomId': 'N',
    'addressFull': 'S',
    'pricePerMonth': 'N',
    'hasWasher': 'BOOL',
    'hasDishwasher': 'BOOL'
}
married_cols = {
    'startAvailability': 'S',
    'endAvailability': 'S'
}
single_cols = {
    'endYear': 'N',
    'endSemester': 'S',
    'isBYUApproved': 'BOOL',
    'numRoommates': 'N'
}


def get_next_room_id():
    client = boto3.client('dynamodb')
    resp = client.get_item(
        TableName=HOUSING_TABLE,
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
    return int(resp['Item']['totalRoomCount']['N']) + 1


def key_exists(key):
    client = boto3.client('dynamodb')
    resp = client.get_item(
        TableName=FILTER_TABLE,
        Key=key
    )
    return 'Item' in resp and len(resp['Item']) > 1

def add_new_room_id(key, room_id):
    client = boto3.client('dynamodb')
    client.update_item(
        Key= key,
        TableName=FILTER_TABLE,
        ExpressionAttributeValues={":inc": {'SS': [room_id]}},
        UpdateExpression="ADD roomIds :inc"
    )


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
        TableName=HOUSING_TABLE,
        ExpressionAttributeValues={":inc": {'N': "1"}},
        UpdateExpression="ADD curRoomCount :inc"
    )

    client.update_item(
        Key={
            'userId': {
                'S': 'count',
            },
            'roomId': {
                'N': '-1'
            }
        },
        TableName=HOUSING_TABLE,
        ExpressionAttributeValues={":inc": {'N': "1"}},
        UpdateExpression="ADD totalRoomCount :inc"
    )


def post_housing(item_data, table):
    client = boto3.client('dynamodb')
    print(item_data)
    # Generate roomId
    client.put_item(
        Item=item_data,
        TableName=table
    )


def make_id(tpe, value):
    if tpe == 'SS':
        return {
            tpe: value
        }
    if tpe != 'BOOL' and type(value) != str:
        value = str(value)
    return {
        tpe: value
    }


def check_data(event, cols):
    for c in cols:
        if c not in event:
            raise NameError('Need to have column')


def get_housing_data(event):
    check_data(event, housing_cols)
    res = {}
    for e in event:
        if e not in housing_cols:
            continue
        res[e] = make_id(housing_cols[e], event[e])
    return res


def add_filter_data(event, cols):
    item_data = get_housing_data(event)
    check_data(event, cols)

    type = 'married' if event['isMarried'] else 'single'
    item_data['type'] = make_id('S', type)
    del event['isMarried']

    for e in event:
        if e in item_data:
            continue
        if e not in cols:
            cols[e] = 'S'
        item_data[e] = make_id(cols[e], event[e])
    return item_data



def generate_primary_key(event, type, cols):
    check_data(event, cols)
    if type == 'single':
        event['isMale'] = 'male' if event['isMale'] else 'female'
        event['isShared'] = 'shared' if event['isShared'] else 'single'
    key_parts = [str(event[col]) for col in cols]
    key = ':'.join(key_parts)
    return {
        "type": make_id("S", type),
        "sortKey": make_id("S", key)
    }


def lambda_handler(event, context):
    success = False
    reason = ''
    if 'isMarried' not in event:
        reason = 'We need to know if it is married or single'
    elif 'userId' not in event:
        reason = 'We need the userId'
    else:
        try:
            type = 'married' if event['isMarried'] else 'single'
            room_id = get_next_room_id()
            print("This is the random RoomId:", room_id)
            cols = married_cols if event['isMarried'] else single_cols
            key_cols = married_key_cols if event['isMarried'] else single_key_cols
            event['roomId'] = room_id
            item_data = add_filter_data(event, cols)
            post_housing(item_data, HOUSING_TABLE)

            primary_key = generate_primary_key(event, type, key_cols)
            if key_exists(primary_key):
                add_new_room_id(primary_key, room_id)
            else:
                primary_key['roomIds'] = make_id('SS', [str(room_id)])
                post_housing(primary_key, FILTER_TABLE)
            update_count()
            success = True
        except NameError as e:
            success = False
            reason = "Errow with the columns"

    return {
        "success": success,
        "reason": reason
    }