import os
import logging

from dotenv import load_dotenv
from mysql.connector import connect, Error as SqlError


async def create_db_connection():
    load_dotenv()
    try:
        connection = connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME')
        )
        connection.autocommit = True
        cur = connection.cursor(dictionary=True)
        return connection, cur

    except SqlError as e:
        logging.error(f"Ошибка при подключении к базе данных: {e}")
        return None, None
