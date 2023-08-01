import mysql.connector

def connect_db():
    mydb = mysql.connector.connect(
       host="localhost",
        user="root",
        password="",
        database="ga"
    )
    return mydb

def execute_query(query, parameters=None):
    mydb = connect_db()
    mycursor = mydb.cursor()
    mycursor.execute(query, parameters)
    results = mycursor.fetchall()
    mydb.commit()
    mydb.close()
    mycursor.close()
    return results