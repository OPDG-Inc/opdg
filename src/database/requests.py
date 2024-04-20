import logging

from mysql.connector import Error
from .models import create_db_connection


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
        logging.error(f"Ошибка: {e}")

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
        logging.error(f"Ошибка: {e}")

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
        logging.error(f"Ошибка: {e}")

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
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()

        return jury_name


async def is_jury_correlate_with_code(jury_id, telegram_id):
    conn = None
    is_correlate = False
    try:
        conn, cur = await create_db_connection()
        query = "SELECT COUNT(*) AS jury_count FROM jury WHERE jury_id = %s AND telegram_id = %s"
        cur.execute(query, (jury_id, telegram_id))

        result = cur.fetchone()
        user_count = result['user_count']

        if user_count > 0:
            is_correlate = True

    except Error as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()

        return is_correlate


async def is_jury(telegram_id):
    conn = None
    is_jury_member = False
    try:
        conn, cur = await create_db_connection()
        query = "SELECT COUNT(*) AS jury_count FROM jury WHERE telegram_id = %s"
        cur.execute(query, (telegram_id,))

        result = cur.fetchone()
        jury_count = result['jury_count']

        if jury_count > 0:
            is_jury_member = True

    except Error as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()

        return is_jury_member


async def is_user(telegram_id):
    conn = None
    is_participants_member = False
    try:
        conn, cur = await create_db_connection()
        query = "SELECT COUNT(*) AS user_count FROM participants WHERE telegram_id = %s"
        cur.execute(query, (telegram_id,))

        result = cur.fetchone()
        user_count = result['user_count']

        if user_count > 0:
            is_participants_member = True

    except Error as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()

        return is_participants_member


async def get_team_name(telegram_id):
    conn = None
    team_name = None

    try:
        conn, cur = await create_db_connection()

        query_participant_id = "SELECT participant_id FROM participants WHERE telegram_id = %s"
        cur.execute(query_participant_id, (telegram_id,))
        result_participant = cur.fetchone()

        if result_participant:
            participant_id = result_participant['participant_id']

            query_team_name = "SELECT name FROM sgroups WHERE captain_id = %s"
            cur.execute(query_team_name, (participant_id,))
            result_team_name = cur.fetchone()

            if result_team_name:
                team_name = result_team_name['name']

    except Error as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()
        return team_name
