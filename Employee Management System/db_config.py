import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(dotenv_path=Path(__file__).parent / '.env')

if not os.getenv('DB_PASSWORD'):
    raise SystemExit("DB_PASSWORD is not set. Copy .env.example to .env and fill it in.")

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'employee_app'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'employee_management')
}

def initialize_database():
    """Initialize the database using the SQL file"""
    try:
        # First, create connection without database
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'employee_app'),
            password=os.getenv('DB_PASSWORD')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            failed = 0
            
            # Read and execute the SQL file
            with open(Path(__file__).parent / 'employee_management.sql', 'r') as sql_file:
                # Split the file into individual statements
                sql_commands = sql_file.read().split(';')
                
                # Execute each statement
                for command in sql_commands:
                    if command.strip():
                        try:
                            cursor.execute(command)
                            connection.commit()
                        except Error as e:
                            failed += 1
                            print(f"Error executing command: {e}")
                            print(f"Command was: {command}")
            
            print("Database initialized successfully!" if failed == 0
                  else f"Initialization finished with {failed} failed statement(s).")
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"Error initializing database: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Initialize the database when the module is run directly
if __name__ == "__main__":
    if input("This DROPS and recreates the database. Type YES to continue: ").strip().upper() == "YES":
        initialize_database()