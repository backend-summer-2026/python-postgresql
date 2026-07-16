"""
============================================================
 ONLAYN DO'KON — psycopg2 bilan ishlash (amaliy)
============================================================
Bu skript PostgreSQL'ga psycopg2 orqali ulanadi va bir nechta
jadval + JOIN'lar bilan ishlashni ko'rsatadi.

Ishga tushirishdan oldin:
  1) pip install psycopg2-binary
  2) Bazani tayyorlang:
       createdb dokon
       psql -d dokon -f 01_schema.sql -f 02_seed.sql
  3) Pastdagi DB_CONFIG'ni o'zingizning sozlamalarga moslang.
  4) python app_psycopg2.py
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# --- Ulanish sozlamalari (o'zingiznikiga moslang) ---
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "dokon_db",
    "user":     "djumanov",
    "password": "Djcoder1120",   # o'z parolingiz
}


def get_connection():
    """PostgreSQL'ga ulanish ochadi."""
    return psycopg2.connect(**DB_CONFIG)


# ------------------------------------------------------------
# 1) Oddiy SELECT + INNER JOIN: har bir buyurtma qaysi mijozniki
# ------------------------------------------------------------
def buyurtmalar_va_mijozlar(conn):
    sql = """
        SELECT o.id AS order_id, c.full_name, o.order_date, o.status
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        ORDER BY o.id;
    """
    with conn.cursor() as cur:          # cursor — so'rov bajaruvchi "kursor"
        cur.execute(sql)
        rows = cur.fetchall()           # barcha qatorlarni ro'yxat sifatida oladi

    print("\n== Buyurtmalar va mijozlar (INNER JOIN) ==")
    for order_id, name, date, status in rows:
        print(f"  #{order_id:>2} | {name:<18} | {date} | {status}")


# ------------------------------------------------------------
# 2) 3 ta jadval JOIN + parametr: bitta buyurtma tafsiloti
#    DIQQAT: qiymatni SQL'ga %s orqali beramiz (SQL injection'dan himoya)
# ------------------------------------------------------------
def buyurtma_tafsiloti(conn, order_id: int):
    sql = """
        SELECT p.name, oi.quantity, oi.unit_price,
               oi.quantity * oi.unit_price AS satr_summasi
        FROM order_items oi
        JOIN products p ON p.id = oi.product_id
        WHERE oi.order_id = %s
        ORDER BY p.name;
    """
    with conn.cursor() as cur:
        cur.execute(sql, (order_id,))   # (order_id,) — parametrlar HAR DOIM tuple
        rows = cur.fetchall()
    print(f"\n== #{order_id}-buyurtma tarkibi ==")
    jami = 0
    for name, qty, price, summa in rows:
        print(f"  {name:<20} {qty} x {price:>10} = {summa:>12}")
        jami += summa
    print(f"  {'JAMI':<20} {'':>16} {jami:>12}")


# ------------------------------------------------------------
# 3) LEFT JOIN + GROUP BY: har bir mijozning buyurtmalari soni
#    RealDictCursor — qatorlarni dict ko'rinishida qaytaradi (row['ustun'])
# ------------------------------------------------------------
def mijozlar_statistikasi(conn):
    sql = """
        SELECT c.full_name,
               COUNT(o.id)                              AS buyurtmalar_soni,
               COALESCE(SUM(oi.quantity*oi.unit_price),0) AS jami_xarid
        FROM customers c
        LEFT JOIN orders      o  ON o.customer_id = c.id AND o.status <> 'cancelled'
        LEFT JOIN order_items oi ON oi.order_id   = o.id
        GROUP BY c.id, c.full_name
        ORDER BY jami_xarid DESC;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    print("\n== Mijozlar statistikasi (LEFT JOIN + GROUP BY) ==")
    for r in rows:
        print(f"  {r['full_name']:<18} | buyurtma: {r['buyurtmalar_soni']} "
              f"| jami: {r['jami_xarid']}")


# ------------------------------------------------------------
# 4) Yozish (INSERT) + tranzaksiya: yangi buyurtma qo'shish
#    Bir nechta INSERT birgalikda bajariladi -> commit yoki rollback
# ------------------------------------------------------------
def yangi_buyurtma_qosh(conn, customer_id: int, savat: list[tuple]):
    """savat = [(product_id, quantity), ...]"""
    try:
        with conn.cursor() as cur:
            # 4.1 buyurtma yaratamiz va uning id'sini olamiz (RETURNING)
            cur.execute(
                "INSERT INTO orders (customer_id, status) VALUES (%s, 'new') RETURNING id;",
                (customer_id,),
            )
            new_order_id = cur.fetchone()[0]

            # 4.2 har bir mahsulot uchun narxni bazadan olib, satr qo'shamiz
            for product_id, qty in savat:
                cur.execute("SELECT price FROM products WHERE id = %s;", (product_id,))
                price = cur.fetchone()[0]
                cur.execute(
                    """INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                       VALUES (%s, %s, %s, %s);""",
                    (new_order_id, product_id, qty, price),
                )
        conn.commit()   # hammasi muvaffaqiyatli -> saqlaymiz
        print(f"\n== Yangi buyurtma yaratildi: #{new_order_id} ==")
        return new_order_id
    except Exception as e:
        conn.rollback()  # xato bo'lsa -> hamma o'zgarishni bekor qilamiz
        print("Xatolik, buyurtma bekor qilindi:", e)
        raise


def main():
    # 'with' bloki tranzaksiyani boshqaradi va ulanishni yopadi
    with get_connection() as conn:
        # buyurtmalar_va_mijozlar(conn)
        # buyurtma_tafsiloti(conn, order_id=1)
        mijozlar_statistikasi(conn)

        # # yangi buyurtma qo'shib ko'ramiz (Bekzod, id=3):
        # # 2 dona sichqoncha (id=2) va 1 dona USB kabel (id=7)
        # yangi_buyurtma_qosh(conn, customer_id=3, savat=[(2, 2), (7, 1)])
        # mijozlar_statistikasi(conn)   # Bekzod summasi o'zgarganini ko'rasiz


if __name__ == "__main__":
    main()
