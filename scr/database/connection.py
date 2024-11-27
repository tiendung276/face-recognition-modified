import pyodbc

server = r"desktop-5cqeviu"  # Replace with your actual server name
driver_name = "SQL Server"  # Replace with the actual driver installed on your machine
database_name = "QuanLyNhanSu"
username = "sa"
password = "123456"

# Define the connection string
connection_str = f"""
    DRIVER={{{driver_name}}};
    SERVER={server};
    DATABASE={database_name};
    UID={username};
    PWD={password};
"""

def get_connection():
    try:
        conn = pyodbc.connect(connection_str)
        # print("Connection successful!")
        return conn
    except pyodbc.Error as e:
        print("Error in connection:", e)
        return None

def close_connection(conn):
    if conn:
        conn.close()
