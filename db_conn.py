import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="mealmate"
    )
    if connection.is_connected():
        print("Connected to MySQL database")
        connection.close()
    else:
        print("Connection failed")
except Exception as e:
    print(f"Error: {e}")
