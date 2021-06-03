from dependencies import mysql
from dependencies.mysql.connector import Error

#aws lambda update-function-code --function-name ProvoUserLogin --zip-file fileb://login.zip


def connect():
    cnx = None
    try:
        cnx = mysql.connector.connect(user='admin', passwd='ProvoHousing452!',
                                    host='provo-housing.cqot4b4a9lbm.us-east-2.rds.amazonaws.com',
                                    database = 'provohousing')
        cnx.autocommit = True
        print("successful connection")
    except Error as e:
        print("error connecting", e)
    return cnx

def register(userId, firstname, lastname, pwd, email, phone, cnx):
    cursor = cnx.cursor()
    query = "INSERT INTO Users(userId, firstName, lastName, password, email, phone) " \
    f"VALUES('{userId}', '{firstname}', '{lastname}', '{pwd}', '{email}', '{phone}');"
    print(query)
    cursor.execute(query)
    cnx.commit()
    return "success"

def lambda_handler(event, context):
    connection = connect()
    if not connection:
        token = ''
    else:
        success = register(event['userId'], event['firstName'], event['lastName'], event['password'], event['email'], event['phone'], connection)
        token = 'true' if success else 'false'
    return {
        'authToken': token
    }