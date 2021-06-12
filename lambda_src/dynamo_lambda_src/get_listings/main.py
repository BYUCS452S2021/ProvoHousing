import boto3

HOUSING_TABLE = 'Housing'
FILTER_TABLE = 'FilterHousing'

s_f_S = {'type': {'S': 'single', },
         'sortKey': {'S': "female:single"}}
s_m_S = {'type': {'S': 'single', },
         'sortKey': {'S': "male:single"}}
s_f_Sh = {'type': {'S': 'single', },
          'sortKey': {'S': "female:shared"}}
s_m_Sh = {'type': {'S': 'single', },
          'sortKey': {'S': "male:shared"}}

singleDict = {"male": {"shared": [s_m_Sh],
                       "single": [s_m_S],
                       "both": [s_m_S, s_m_Sh]},
              "female": {"shared": [s_f_Sh],
                         "single": [s_f_S],
                         "both": [s_f_S, s_f_Sh]},
              "all": [s_m_S, s_m_Sh, s_f_S, s_f_Sh]}


def getMarried(numBedRooms):
    return {'type': {'S': 'married', },
            'sortKey': {'N': int(numBedRooms)}}


def key_exists(key):
    client = boto3.client('dynamodb')
    resp = client.get_item(
        TableName=FILTER_TABLE,
        Key=key
    )
    return 'Item' in resp and len(resp['Item']) > 1


def getRoomIds(keyList):
    client = boto3.client('dynamodb')
    roomList = []

    for key in keyList:
        if key_exists(key):
            resp = client.get_item(
                TableName=FILTER_TABLE,
                Key=key
            )
            roomList.extend(resp['Item']['roomIds']['SS'])
    return roomList


def getRooms(roomList):
    client = boto3.client('dynamodb')
    rooms = []
    for id in roomList:
        idParts = id.split(":")
        resp = client.get_item(
            TableName=HOUSING_TABLE,
            Key={
                'userId': {
                    'S': idParts[1]
                },
                'roomId': {
                    'N': idParts[0]
                }
            }
        )
        rooms.append(resp['Item'])
    return rooms


def lambda_handlerT(event, context):
    return getRooms(['5:mamberly'])
    # getRoomIds(singleDict["all"])


def lambda_handler(event, context):
    success = False
    reason = ''
    rooms = []
    try:
        if event['isMarried']:
            keyList = getMarried(event["numBedrooms"])
            roomList = getRoomIds(keyList)
        else:
            if event['isMale']:
                gType = "male"
            else:
                gType = 'female'
            keyList = singleDict[gType][event['roomType']]
            print(keyList)
            roomList = getRoomIds(keyList)
            print(roomList)
            rooms = getRooms(roomList)

        success = True
    except NameError as e:
        success = False
        reason = "Errow with the columns"

    return rooms
