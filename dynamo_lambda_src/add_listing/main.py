import boto3

HOUSING_TABLE = 'Housing'
FILTER_TABLE = 'FilteredHousing'

housing_cols = {
    'roomId': 'N',
    'addressFull': 'S',
    'pricePerMonth': 'N',
    'hasWasher': 'BOOL',
    'hasDishwasher': 'BOOL'
}
married_cols = {
    'startAvailability': 'S',
    'endAvailability': 'S',
    'numBedrooms': 'N'
}
single_cols = {
    'endYear': 'N',
    'endSemester': 'S',
    'isShared': 'S',
    'isMale': 'S',
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

    # Generate roomId
    client.put_item(
        Item=item_data,
        TableName=table
    )


def make_id(tpe, value):
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


def add_filter_data_married(event):
    item_data = get_housing_data(event)
    check_data(event, married_cols)

    del event['isMarried']

    item_data['type'] = make_id('S', 'married')
    for e in event:
        if e in item_data:
            continue
        if e not in married_cols:
            married_cols[e] = 'S'
        item_data[e] = make_id(married_cols[e], event[e])
    return item_data


def add_filter_data_single(event):
    item_data = get_housing_data(event)
    check_data(event, single_cols)

    item_data['type'] = make_id('S', 'single')

    for e in event:
        if e in item_data or e == 'isMarried':
            continue
        elif e == 'isMale':
            new_title = 'gender'
            val = 'male' if event[e] else 'female'
            item_data[new_title] = make_id(single_cols[e], val)
            continue
        elif e == 'isShared':
            new_title = 'single/shared'
            val = 'shared' if event[e] else 'single'
            item_data[new_title] = make_id(single_cols[e], val)
            continue
        if e not in single_cols:
            single_cols[e] = 'S'
        item_data[e] = make_id(single_cols[e], event[e])
    return item_data


def lambda_handler(event, context):
    success = False
    reason = ''
    if 'isMarried' not in event:
        reason = 'We need to know if it is married or single'
    elif 'userId' not in event:
        reason = 'We need the userId'
    else:
        try:
            room_id = get_next_room_id()
            print("This is the random RoomId:", room_id)
            user_id = event['userId']
            item_data = {
                'roomId': {
                    'N': str(room_id),
                },
                'userId': {
                    'S': user_id,
                },
            }

            post_housing(item_data, HOUSING_TABLE)
            event['roomId'] = room_id
            item_data = add_filter_data_married(event) if event['isMarried'] else add_filter_data_single(event)
            print(item_data)
            post_housing(item_data, FILTER_TABLE)
            update_count()
            success = True
        except NameError as e:
            success = False
            reason = "Errow with the columns"

    return {
        "success": success,
        "reason": reason
    }