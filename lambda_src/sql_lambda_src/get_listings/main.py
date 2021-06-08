from dependencies import mysql
from dependencies.mysql.connector import Error
import json
import datetime

# aws lambda update-function-code --function-name ProvoUserLogin --zip-file fileb://login.zip

date_format = "%Y/%m/%d"


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


def getMarriedListings(search, cnx):
    cursor = cnx.cursor()
    # Inner Join so order doesn't matter
    query = "SELECT * FROM Housing AS h INNER JOIN MarriedHousing AS m ON h.roomId = m.roomId "
    where_clause = getHousingWhereClauses(search)
    query = query + where_clause

    bedroom_clause = '' if 'numBedrooms' not in search else f'numBedroms = {search["numBedrooms"]}'

    if len(bedroom_clause) > 0:
        print(where_clause)
        if where_clause == "":
            query += ' WHERE ' + bedroom_clause
        else:
            query += ' AND ' + bedroom_clause

    query = f"{query} ORDER BY pricePerMonth;"
    print(query)
    cursor.execute(query)
    result = buildJSON(cursor)

    # Add an authToken? Do you have to be logged in to search?

    return result


def getSingleListings(search, cnx):
    # Build Query
    query = "SELECT * FROM Housing AS h JOIN SingleHousing AS s ON h.roomId = s.roomId "
    where_clause = getHousingWhereClauses(search)
    query = query + where_clause

    male_clause = '' if 'isMale' not in search else f"isMale = {int(search['isMale'])}"
    shared_clause = '' if 'shared' not in search else f"isShared = {int(search['isShared'])}"
    roommate_clause = '' if 'numRoommates' not in search else f"numRoommates = {search['numBedroms']}"
    byu_clause = '' if 'isBYUApproved' not in search else f"isBYUApproved = {int(search['isBYUApproved'])}"

    clauses = [male_clause, shared_clause, roommate_clause, byu_clause]
    clauses = [clause for clause in clauses if len(clause) > 0]

    if where_clause != "":
        clause_query = ' AND '.join(clauses)
        query = f"{query} AND {clause_query} ORDER BY pricePerMonth;"
    else:
        if len(clauses) > 0:
            clause_query = ' AND '.join(clauses)
            clause_query = "WHERE " + clause_query
            query = f"{query} {clause_query} ORDER BY pricePerMonth;"
        else:
            query = f"{query} ORDER BY pricePerMonth;"

    # Add semicolon and order by (Or listing date?)

    print(query)
    cursor = cnx.cursor()
    cursor.execute(query)
    result = buildJSON(cursor)

    return result


def getListings(search, cnx):
    where_clause = getHousingWhereClauses(search)
    query = "SELECT * FROM Housing " + where_clause
    cursor = cnx.cursor()
    cursor.execute(query)
    resp = buildJSON(cursor)
    return resp


def getHousingWhereClauses(search):
    # price filter (implemented as slider bars? If not check input types)
    minPrice = None if "minPrice" not in search else search['minPrice']
    maxPrice = None if "maxPrice" not in search else search['maxPrice']
    if minPrice and maxPrice:
        price_clause = f"pricePerMonth BETWEEN {minPrice} AND {maxPrice}"
    elif minPrice:
        price_clause = f"pricePerMonth >= {minPrice}"
    elif maxPrice:
        price_clause = f"pricePerMonth <= {maxPrice}"
    else:
        price_clause = ''

    # for date filters, we assume that we are getting a date object from the http request

    # availability filters
    start = None if "startAvailability" not in search else search['startAvailability']
    end = None if "endAvailabiity" not in search else search['endAvailabiity']
    start_filter = '' if not start else f"startAvailability <= \'{start}\'"
    end_filter = '' if not end else f"endAvailability <= \'{end}\'"

    # contract filters
    end = None if "endContract" not in search else datetime.datetime.strptime(search['endContract'], date_format)
    end_contract_filter = '' if not end else f"endContract <= \'{end}\'"

    # Has a Washer and Dryer in Unit
    washer_clause = '' if 'hasWasher' not in search else f"hasWasher = {int(search['hasWasher'])}"

    # Has a Dishwasher
    dishwasher_clause = '' if 'hasDishwasher' not in search else f"hasDishwasher = {int(search['hasDishwasher'])}"

    # BUILD HERE
    clauses = [price_clause, start_filter, end_filter, end_contract_filter, washer_clause, dishwasher_clause]
    clauses_filter = [clause for clause in clauses if len(clause) > 0]
    where_clause = ' AND '.join(clauses_filter)

    if where_clause is not "":
        return "WHERE " + where_clause
    else:
        return ""


def buildJSON(cur):
    row_headers = [x[0] for x in cur.description]  # this will extract row headers
    rv = cur.fetchall()
    print(f"We received {len(rv)} rows")
    json_data = []
    for result in rv:
        res = {}
        for i in range(len(row_headers)):
            if type(result[i]) == datetime.date:
                res[row_headers[i]] = result[i].strftime(date_format)
            else:
                res[row_headers[i]] = result[i]
        json_data.append(res)
    return json_data


def lambda_handler(event, context):
    connection = connect()
    if not connection:
        print("Failed to get connction")
        listings = []
    else:
        # Check authtoken
        # If invalid return an error
        if 'isMarried' in event:
            listings = getMarriedListings(event, connection) if event['isMarried'] else getSingleListings(event,
                                                                                                          connection)
        else:
            print("No isMarried filter, just getting all listings")
            listings = getListings(event, connection)
    return {
        'listings': listings
    }
