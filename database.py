import psycopg2
import datetime

conn = psycopg2.connect(
    host="ep-quiet-hill-a9m5ai1n-pooler.gwc.azure.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_fbslSOW49ViR",
    port=5432,
    sslmode='require'
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS birthdays (
    user_id INTEGER,
    name TEXT,
    date DATE
)
""")
conn.commit()


def add_birthday(user_id, name, date):
    try:
        cursor.execute(
            "INSERT INTO birthdays (user_id, name, date) VALUES (%s, %s, %s)",
            (user_id, name, date)
        )
        conn.commit()

    except Exception as e:
        print("SQL error:", e)
        conn.rollback()


def get_all_user_ids():
    try:
        cursor.execute("SELECT DISTINCT user_id FROM birthdays")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print("SQL error:", e)
        conn.rollback()


def get_birthdays(user_id):
    try:
        cursor.execute("SELECT name, date FROM birthdays WHERE user_id = %s", (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print("SQL error:", e)
        conn.rollback()


def get_birthdays_today(today_date):
    try:
        cursor.execute("""SELECT user_id, name FROM birthdays WHERE TO_CHAR(date, 'MM-DD') = %s """, (today_date,))
        return cursor.fetchall()
    except Exception as e:
        print("SQL error:", e)
        conn.rollback()


def delete_birthday(user_id, name):
    try:
        cursor.execute("DELETE FROM birthdays WHERE user_id = %s AND name = %s", (user_id, name))
        conn.commit()
    except Exception as e:
        print("SQL error:", e)
        conn.rollback()