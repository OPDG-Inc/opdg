from .models import create_db_connection


async def is_user_not_exists(telegram_id):
    conn, cur = await create_db_connection()
    query = "SELECT COUNT(*) AS user_count FROM participants WHERE telegram_id = %s"
    cur.execute(query, (telegram_id,))

    result = cur.fetchone()['user_count']
    is_not_exists = False if result else True

    return is_not_exists


async def get_jury_by_link_code(code):
    conn, cur = await create_db_connection()
    query = "SELECT jury_id AS result FROM jury WHERE pass_phrase = %s"
    cur.execute(query, (code,))

    jury_id = cur.fetchone()['result']

    return jury_id


async def get_jury_status(jury_id):
    conn, cur = await create_db_connection()
    query = "SELECT status AS result FROM jury WHERE jury_id = %s"
    cur.execute(query, (jury_id,))

    status = cur.fetchone()['result']

    return status


async def change_jury_status_to_registered(jury_id):
    conn, cur = await create_db_connection()
    query = "UPDATE jury SET status = 'registered' WHERE  jury_id = %s"
    cur.execute(query, (jury_id,))


async def get_jury_name(jury_id):
    conn, cur = await create_db_connection()
    query = "SELECT name AS result FROM jury WHERE  jury_id = %s"
    cur.execute(query, (jury_id,))

    jury_name = cur.fetchone()['result']

    return jury_name
