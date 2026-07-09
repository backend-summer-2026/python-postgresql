import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Connect to your postgres DB
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
)

def delete_users() -> None:
    cur = conn.cursor()
    cur.execute("DELETE FROM users")


def add_user(name: str, age: int) -> None:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, age) VALUES (%s, %s)",
        (name, age),
    )
    conn.commit()


def get_all_users() -> list[tuple]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")

    records = cur.fetchall()
    return records


def update_user(name: str, age: int) -> None:
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET name = %s WHERE age = %s",
        (name, age),
    )
    conn.commit()


def main() -> None:
    # delete_users()

    name = 'ali'
    age = 10
    # add_user(name, age)

    update_user(name, age)

    users = get_all_users()
    for user in users:
        print(user)

if __name__ == '__main__':
    main()

