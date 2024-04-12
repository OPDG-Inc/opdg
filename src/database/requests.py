from .models import create_db_connection


async def is_not_exists(telegram_id):
    conn, cur = await create_db_connection()
    sql = "SELECT COUNT(*) AS user_count FROM participants WHERE telegram_id = %s"
    cur.execute(sql, (telegram_id,))

    result = cur.fetchone()['user_count']
    is_user_not_exists = False if result else True

    return is_user_not_exists
