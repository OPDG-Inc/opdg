from mysql.connector import Error
from .models import create_db_connection


async def is_user_not_exists(telegram_id):
    conn = None
    is_not_exists = False
    try:
        conn, cur = await create_db_connection()
        query = "SELECT COUNT(*) AS user_count FROM participants WHERE telegram_id = %s"
        cur.execute(query, (telegram_id,))

        result = cur.fetchone()
        user_count = result['user_count']

        if user_count == 0:
            is_not_exists = True

    except Error as e:
        print(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()

        return is_not_exists


async def get_jury_by_link_code(code):
    conn = None
    jury_id = None
    try:
        conn, cur = await create_db_connection()
        query = "SELECT jury_id AS result FROM jury WHERE pass_phrase = %s"
        cur.execute(query, (code,))

        result = cur.fetchone()
        if result:
            jury_id = result['result']

    except Error as e:
        print(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()

        return jury_id


async def get_jury_status(jury_id):
    conn = None
    status = None
    try:
        conn, cur = await create_db_connection()
        query = "SELECT status AS result FROM jury WHERE jury_id = %s"
        cur.execute(query, (jury_id,))

        result = cur.fetchone()
        if result:
            status = result['result']

    except Error as e:
        print(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()
        return status


async def set_jury_status_to_registered(jury_id):
    conn = None
    try:
        conn, cur = await create_db_connection()
        query = "UPDATE jury SET status = %s WHERE jury_id = %s"
        cur.execute(query, ('registered', jury_id,))

    except Error as e:
        print(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()


async def get_jury_name(jury_id):
    conn = None
    jury_name = None
    try:
        conn, cur = await create_db_connection()
        query = "SELECT name AS result FROM jury WHERE jury_id = %s"
        cur.execute(query, (jury_id,))

        result = cur.fetchone()
        if result:
            jury_name = result['result']

    except Error as e:
        print(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()

        return jury_name
