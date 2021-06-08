from dependencies import mysql
from dependencies.mysql.connector import Error
from datetime import datetime

# aws lambda update-function-code --function-name ProvoUserLogin --zip-file fileb://login.zip

housing_cols = ['addressFull', 'pricePerMonth', 'startAvailability', 'endAvailability', 'endContract', 'hasWasher',
                'hasDishwasher', 'photoLink']
married_cols = ['roomId', 'numBedrooms']
single_cols = ['roomId', 'numRoommates', 'isShared', 'isMale', 'isBYUApproved']
listing_cols = ['userId', 'roomId', "listingDate", "showPhoneOnListing"]

HOUSING_TABLE = "Housing"
MARRIED_TABLE = "MarriedHousing"
SINGLE_TABLE = "SingleHousing"
LISTINGS_TABLE = "Listings"


def connect():
    cnx = None
    try:
        cnx = mysql.connector.connect(user='admin', passwd='ProvoHousing452!',
                                      host='provo-housing.cqot4b4a9lbm.us-east-2.rds.amazonaws.com',
                                      database='provohousing')
        cnx.autocommit = True
        print("successful connection")
    except Error as e:
        print("error connecting", e)
    return cnx


def create_insert_query(events, table, cols):
    given_cols = [col for col in events if col in cols]
    vals = [f"\'{events[col]}\'" for col in events if col in cols]
    cols_str = ', '.join(given_cols)
    vals_str = ', '.join(vals)
    query = f"INSERT INTO {table} ({cols_str})\nVALUES({vals_str});"
    return query


def create_query(events):
    given_cols = [col for col in events if col in housing_cols]
    vals = [f"\'{events[col]}\'" for col in events if col in housing_cols]
    where_clause = ""
    for i in range(len(given_cols)):
        where_clause += given_cols[i] + " = " + vals[i]
        if i != len(given_cols) - 1:
            where_clause += ' AND '
    query = f"SELECT roomId FROM {HOUSING_TABLE} WHERE {where_clause};"
    return query


def add_listing(cnx, query):
    cursor = cnx.cursor()
    cursor.execute(query)


def get_room_id(cnx, query):
    cursor = cnx.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 1:
        room_id = results[0][0]
        return room_id


def clean_bools(event):
    for k, v in event.items():
        if type(v) == bool:
            event[k] = int(v)


def lambda_handler(event, context):
    if 'userId' not in event:
        return {
            'success': False,
            'reason': "Need user id"
        }
    clean_bools(event)
    connection = connect()
    insert_query = create_insert_query(event, HOUSING_TABLE, housing_cols)
    print(insert_query)
    add_listing(connection, insert_query)
    query = create_query(event)
    print(query)
    room_id = get_room_id(connection, query)
    if not room_id:
        return {
            "success": False,
            "reason": "Trouble creating housing"
        }
    if 'isMarried' in event:
        event['roomId'] = room_id
        query = create_insert_query(event, MARRIED_TABLE, married_cols) if event['isMarried'] else create_insert_query(
            event, SINGLE_TABLE, single_cols)
        print(query)
        add_listing(connection, query)

    user_id = event['userId']
    today = datetime.today()
    event['listingDate'] = today.strftime("%Y/%m/%d")
    query = create_insert_query(event, LISTINGS_TABLE, listing_cols)
    add_listing(connection, query)
    return {
        "success": True,
        "roomId": room_id
    }
