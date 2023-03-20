import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
}

DB_NAME = os.getenv('DB_NAME')

def get_db_connection(database=None):
    if database:
        config = {**db_config, 'database': database}
    else:
        config = db_config
    return mysql.connector.connect(**config)

def create_database():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
    cursor.close()
    connection.close()

def create_users_table():
    connection = get_db_connection(database=DB_NAME)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            join_date DATETIME,
            has_established_role BOOLEAN
        );
    """)
    cursor.close()
    connection.close()

def create_add_user_function():
    connection = get_db_connection(database=DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        DROP PROCEDURE IF EXISTS add_user;
    """)

    cursor.execute("""
        CREATE PROCEDURE add_user(
            IN p_user_id BIGINT,
            IN p_join_date DATETIME,
            IN p_has_established_role BOOLEAN
        )
        BEGIN
            INSERT INTO users (user_id, join_date, has_established_role)
            VALUES (p_user_id, p_join_date, p_has_established_role);
        END;
    """)

    cursor.close()
    connection.close()

def create_update_user_function():
    connection = get_db_connection(database=DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        DROP PROCEDURE IF EXISTS update_user;
    """)

    cursor.execute("""
        CREATE PROCEDURE update_user(
            IN p_user_id BIGINT,
            IN p_has_established_role BOOLEAN
        )
        BEGIN
            UPDATE users
            SET has_established_role = p_has_established_role
            WHERE user_id = p_user_id;
        END;
    """)

    cursor.close()
    connection.close()

if __name__ == "__main__":
    create_database()
    create_users_table()
    create_add_user_function()
    create_update_user_function()
