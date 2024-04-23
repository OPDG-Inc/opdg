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


async def get_jury_full_name(jury_id):
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
    group_id = await get_group_id_by_captain(telegram_id)
    try:
        conn, cur = await create_db_connection()

        query_team_name = "SELECT name FROM sgroups WHERE group_id = %s"
        cur.execute(query_team_name, (group_id,))
        result_team_name = cur.fetchone()

        if result_team_name:
            team_name = result_team_name['name']

    except Error as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()
        return team_name


async def get_group_id_by_captain(telegram_id):
    conn = None
    group_id = None

    try:
        conn, cur = await create_db_connection()

        query_captain_id = "SELECT participant_id FROM participants WHERE telegram_id = %s AND status = %s"
        cur.execute(query_captain_id, (telegram_id, 'captain',))
        result_captain = cur.fetchone()

        if result_captain:
            captain_id = result_captain['participant_id']

            query_group_id = "SELECT group_id FROM sgroups WHERE captain_id = %s"
            cur.execute(query_group_id, (captain_id,))
            result_group_id = cur.fetchone()

            if result_group_id:
                group_id = result_group_id['group_id']

    except Error as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()
        return group_id


async def set_video_url_and_status_to_uploaded(telegram_id, public_url):
    conn = None
    group_id = await get_group_id_by_captain(telegram_id)
    try:
        conn, cur = await create_db_connection()
        query = "UPDATE sgroups SET video_status = %s, video_link = %s WHERE group_id = %s"
        cur.execute(query, ('uploaded', public_url, group_id,))

    except Error as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()
