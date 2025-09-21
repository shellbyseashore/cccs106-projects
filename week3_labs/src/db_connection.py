import mysql.connector
from mysql.connector import Error

def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Replace with your actual MySQL root password
            database="fletapp"
        )
        if connection.is_connected():
            print("Connection successful!")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
