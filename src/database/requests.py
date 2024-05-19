import logging

from mysql.connector import Error
from .models import create_db_connection


async def get_jury_id_by_link_code(code):
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


async def get_jury_id_status(jury_id):
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


async def get_team_name_by_captain(telegram_id):
    group_id = await get_group_id_by_captain(telegram_id)
    conn = None
    team_name = None
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


async def get_team_name_by_group_id(group_id):
    conn = None
    team_name = None
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


async def get_team_video_link(group_id):
    conn = None
    video_link = None
    try:
        conn, cur = await create_db_connection()

        query_video_link = "SELECT video_link FROM sgroups WHERE group_id = %s"
        cur.execute(query_video_link, (group_id,))
        result_video_link = cur.fetchone()

        if result_video_link:
            video_link = result_video_link['video_link']

    except Error as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()
        return video_link


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
    group_id = await get_group_id_by_captain(telegram_id)
    conn = None
    try:
        conn, cur = await create_db_connection()
        query = "UPDATE sgroups SET video_status = %s, video_link = %s WHERE group_id = %s"
        cur.execute(query, ('uploaded', public_url, group_id,))

    except Error as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()


async def is_video_status_uploaded(telegram_id):
    group_id = await get_group_id_by_captain(telegram_id)
    conn = None
    video_status = None
    is_uploaded = False
    try:
        conn, cur = await create_db_connection()
        query = "SELECT video_status FROM sgroups WHERE group_id = %s"
        cur.execute(query, (group_id,))

        result = cur.fetchone()
        if result:
            video_status = result['video_status']

        if video_status == 'uploaded':
            is_uploaded = True

    except Error as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()
        return is_uploaded


async def get_jury_id_by_telegram_id(telegram_id):
    conn = None
    jury_id = None
    try:
        conn, cur = await create_db_connection()
        query = "SELECT jury_id AS result FROM jury WHERE telegram_id = %s"
        cur.execute(query, (telegram_id,))

        result = cur.fetchone()
        if result:
            jury_id = result['result']

    except Error as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            conn.close()
        return jury_id


async def get_rated_videos_by_jury(telegram_id):
    conn = None
    rated_videos = []

    try:
        conn, cur = await create_db_connection()
        jury_id = await get_jury_id_by_telegram_id(telegram_id)
        if jury_id is None:
            return rated_videos

        query = "SELECT group_id FROM marks WHERE jury_id = %s"
        cur.execute(query, (jury_id,))
        results = cur.fetchall()

        for row in results:
            rated_videos.append(row['group_id'])

    except Exception as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            await conn.close()
        return rated_videos


async def get_all_group_with_uploaded_videos():
    conn = None
    uploaded_videos = []

    try:
        conn, cur = await create_db_connection()

        query = "SELECT group_id FROM sgroups WHERE video_status = %s AND video_link IS NOT NULL"
        await cur.execute(query, ('uploaded',))
        results = await cur.fetchall()

        for row in results:
            uploaded_videos.append(row['group_id'])

    except Exception as e:
        logging.error(f"Ошибка: {e}")

    finally:
        if conn is not None:
            await conn.close()
        return uploaded_videos
