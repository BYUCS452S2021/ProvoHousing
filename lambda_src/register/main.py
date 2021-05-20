from dependencies import mysql
from dependencies.mysql.connector import Error

#aws lambda update-function-code --function-name ProvoUserLogin --zip-file fileb://login.zip


def connect():
    cnx = None
    try:
        cnx = mysql.connector.connect(user='admin', passwd='ProvoHousing452!',
                                      host='provohousing.cqot4b4a9lbm.us-east-2.rds.amazonaws.com',
                                      database = 'provo-housing')
        cnx.autocommit = True
        print("successful connection")
    except Error as e:
        print("error connecting", e)
    return cnx

def login(userId, pwd, cnx):
    cursor = cnx.cursor()
    query = f"SELECT password FROM Users WHERE userId = '{userId}'"
    cursor.execute(query)
    result = cursor.fetchall()
    if not result or len(result) == 0:
        return False
    db_pwd = result[0][0]
    return db_pwd == pwd

def lambda_handler(event, context):
    connection = connect()
    if not connection:
        token = ''
    else:
        success = login(event['userId'], event['password'], connection)
        token = 'true' if success else 'false'
    return {
        'authToken': token
    }

if __name__ == '__main__':
    print(lambda_handler({
        'userId': 'mamberly',
        'password': 'test'
    }, None))
