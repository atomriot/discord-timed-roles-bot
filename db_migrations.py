import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def create_database():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")

    cursor.close()
    connection.close()

def create_users_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            join_date DATETIME NOT NULL,
            has_established_role TINYINT NOT NULL
        )
    """)

    # Create add_user procedure
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.routines
        WHERE routine_schema = DATABASE()
        AND routine_name = 'add_user'
    """)
    stored_procedure_exists = cursor.fetchone()[0]

    if not stored_procedure_exists:
        cursor.execute("""
            CREATE PROCEDURE add_user(IN p_user_id BIGINT, IN p_join_date DATETIME, IN p_has_established_role TINYINT)
            BEGIN
                INSERT INTO users (user_id, join_date, has_established_role)
                VALUES (p_user_id, p_join_date, p_has_established_role);
            END
        """)

    # Create update_user procedure
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.routines
        WHERE routine_schema = DATABASE()
        AND routine_name = 'update_user'
    """)
    stored_procedure_exists = cursor.fetchone()[0]

    if not stored_procedure_exists:
        cursor.execute("""
            CREATE PROCEDURE update_user(IN p_user_id BIGINT, IN p_has_established_role TINYINT)
            BEGIN
                UPDATE users
                SET has_established_role = p_has_established_role
                WHERE user_id = p_user_id;
            END
        """)

    cursor.close()
    connection.close()

def create_run_status_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS run_status (
            id INT AUTO_INCREMENT PRIMARY KEY,
            run_date DATETIME NOT NULL,
            num_users_updated INT NOT NULL,
            status ENUM('success', 'failure') NOT NULL,
            error_message TEXT
        )
    """)

    # Create add_run_status procedure
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.routines
        WHERE routine_schema = DATABASE()
        AND routine_name = 'add_run_status'
    """)
    stored_procedure_exists = cursor.fetchone()[0]

    if not stored_procedure_exists:
        cursor.execute("""
            CREATE PROCEDURE add_run_status(IN p_run_date DATETIME, IN p_num_users_updated INT, IN p_status ENUM('success', 'failure'), IN p_error_message TEXT)
            BEGIN
                INSERT INTO run_status (run_date, num_users_updated, status, error_message)
                VALUES (p_run_date, p_num_users_updated, p_status, p_error_message);
            END
        """)

    cursor.close()
    connection.close()

create_database()
create_users_table()
create_run_status_table()
