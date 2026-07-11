import os
import random

import psycopg2
from psycopg2.extensions import connection as PgConnection
from dotenv import load_dotenv

load_dotenv()


def get_connection() -> PgConnection:
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
    )


def create_users_table(conn: PgConnection) -> None:
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id SERIAL UNIQUE,
            name VARCHAR(128) NOT NULL,
            username VARCHAR(64) NOT NULL UNIQUE
        )"""
    )

    conn.commit()


def create_profile_table(conn: PgConnection) -> None:
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS profiles (
            id SERIAL UNIQUE,
            bio VARCHAR(128),
            user_id INTEGER REFERENCES users(id) UNIQUE
        )"""
    )

    conn.commit()


def create_orders_table(conn: PgConnection) -> None:
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS orders (
            id SERIAL UNIQUE,
            user_id INTEGER REFERENCES users(id)
        )"""
    )

    conn.commit()


def insert_random_users(conn: PgConnection) -> None:
    cursor = conn.cursor()

    first_names = ["Ali", "Vali", "Hasan", "Husan", "Olim", "Karim", "Aziz", "Bekzod", "Diyor", "Sardor"]
    last_names = ["Aliyev", "Valiyev", "Karimov", "Olimov", "Azizov", "Bekov", "Sodiqov", "Toshev", "Rahimov", "Usmonov"]

    for _ in range(10):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        username = f"user_{random.randint(100000, 999999)}"

        cursor.execute(
            "INSERT INTO users (name, username) VALUES (%s, %s)",
            (name, username),
        )

    conn.commit()


def insert_random_orders(conn: PgConnection) -> None:
    cursor = conn.cursor()

    for _ in range(52346):
        cursor.execute(
            "INSERT INTO orders (user_id) VALUES (%s)",
            (random.randint(1, 20), )
        )

    conn.commit()


def show_users(conn: PgConnection) -> None:
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()
    for user in users:
        print(user)


def show_user(user_id: int, conn: PgConnection) -> None:
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id, ))

    user = cursor.fetchone()
    print(user)


def show_orders(conn: PgConnection) -> None:
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders")

    orders = cursor.fetchall()
    for order in orders:
        print(order)


def show_orders_by_user(user_id: int, conn: PgConnection) -> None:
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id, ))

    orders = cursor.fetchall()
    for order in orders:
        print(order)


def get_count_of_orders(conn: PgConnection) -> int | None:
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM orders")

    result = cursor.fetchone()
    if result is not None:
        return result[0]


def main() -> None:
    try:
        create_users_table(get_connection())
        create_orders_table(get_connection())
        # insert_random_users(get_connection())
        # insert_random_orders(get_connection())
        # show_users(get_connection())
        # n = get_count_of_orders(get_connection())
        # print(n)
        # show_orders(get_connection())
        # show_user(3, get_connection())
        show_orders_by_user(3, get_connection())

    except psycopg2.Error:
        print("SQL STATEMENT XATO")

if __name__ == '__main__':
    main()
