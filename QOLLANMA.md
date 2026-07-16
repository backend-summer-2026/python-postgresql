# Python + PostgreSQL — Relationship va JOIN amaliyoti

Onlayn do'kon misolida bir nechta jadval bilan ishlash. Ikkita yondashuv:
**psycopg2** (sof SQL) va **SQLAlchemy** (ORM — model'lar orqali).

---

## 1. Loyiha tarkibi

| Fayl | Vazifasi |
|------|----------|
| `01_schema.sql` | Jadvallar va relationship'lar (CREATE TABLE) |
| `02_seed.sql` | Namunaviy ma'lumotlar (INSERT) |
| `03_queries.sql` | 10 ta tayyor JOIN so'rovi (psql'da sinash uchun) |
| `app_psycopg2.py` | psycopg2 bilan ishlaydigan skript |
| `app_sqlalchemy.py` | SQLAlchemy (ORM) bilan ishlaydigan skript |
| `MASHQLAR.md` | Mustaqil bajarish uchun mashqlar + yechimlar |

---

## 2. O'rnatish va ishga tushirish

```bash
# 1) Kutubxonalar
pip install psycopg2-binary sqlalchemy

# 2) Baza yaratish
createdb dokon

# 3) Jadval va ma'lumotlarni yuklash
psql -d dokon -f 01_schema.sql
psql -d dokon -f 02_seed.sql

# 4) Skriptlarni ishga tushirish
python app_psycopg2.py
python app_sqlalchemy.py
```

> Skript ichidagi ulanish sozlamalarini (`host`, `user`, `password`, `dbname`)
> o'zingiznikiga moslashtiring.

---

## 3. Jadvallar va relationship'lar

```
customers (mijozlar)  1 ──────< orders (buyurtmalar)
                                   │ 1
                                   │
                                   ˅ ko'p
products (mahsulotlar) 1 ──────< order_items (buyurtma satrlari)
```

Uchta asosiy bog'lanish turi:

**One-to-many (bir-ko'p)** — eng ko'p uchraydigani. Bitta mijozda ko'p
buyurtma bo'ladi, lekin har bir buyurtma faqat bitta mijozga tegishli.
Buni "ko'p" tarafdagi jadvalga **foreign key** (`orders.customer_id`)
qo'yish orqali quramiz.

**Many-to-many (ko'p-ko'p)** — bitta buyurtmada ko'p mahsulot, bitta
mahsulot ko'p buyurtmada bo'lishi mumkin. Buni to'g'ridan-to'g'ri bog'lab
bo'lmaydi, shuning uchun oradagi **bog'lovchi (junction) jadval**
`order_items` ishlatiladi. U ikkala tarafga ham foreign key beradi
(`order_id` va `product_id`) va qo'shimcha ma'lumot saqlaydi (nechta, qanchadan).

**Foreign key nima beradi?** Ma'lumot yaxlitligini kafolatlaydi: mavjud
bo'lmagan mijozga buyurtma yozib bo'lmaydi. `ON DELETE CASCADE` — mijoz
o'chirilsa, uning buyurtmalari ham o'chadi.

---

## 4. JOIN turlari (qisqacha)

JOIN — bu ikki jadvalni umumiy ustun (odatda foreign key) orqali
bitta natijaga birlashtirish.

**INNER JOIN** — faqat ikkala tarafda ham mos keladigan qatorlar.
Buyurtma qilmagan mijoz chiqmaydi.

```sql
SELECT o.id, c.full_name
FROM orders o
JOIN customers c ON c.id = o.customer_id;
```

**LEFT JOIN** — chap jadvalning HAMMA qatori chiqadi; o'ng tarafda mos
qator bo'lmasa `NULL` bilan to'ldiriladi. "Kim hech narsa sotib olmagan?"
kabi savollarga aynan shu kerak.

```sql
SELECT c.full_name, o.id
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id;
-- buyurtmasi yo'q mijozda o.id = NULL
```

**LEFT JOIN + IS NULL** — "bog'lanmagan"larni topishning klassik usuli:

```sql
SELECT c.full_name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;   -- umuman buyurtma qilmaganlar
```

Amalda 90% holatda shu uchtasi (INNER, LEFT, LEFT+IS NULL) yetadi.
`RIGHT JOIN` va `FULL JOIN` kamdan-kam kerak bo'ladi.

---

## 5. psycopg2 asoslari

psycopg2 — SQL'ni o'zingiz yozasiz, natijani Python'da olasiz. To'liq nazorat.

```python
import psycopg2

conn = psycopg2.connect(host="localhost", dbname="dokon",
                        user="postgres", password="...")
cur = conn.cursor()               # kursor — so'rov bajaruvchi
cur.execute("SELECT * FROM customers WHERE city = %s;", ("Toshkent",))
rows = cur.fetchall()             # barcha qatorlar ro'yxati
conn.commit()                     # yozish so'rovlaridan keyin shart
conn.close()
```

Eng muhim 4 qoida:

1. **Parametrni HAR DOIM `%s` orqali bering**, matnni qo'lda ulamang.
   To'g'ri: `cur.execute("... WHERE id = %s", (5,))`.
   Noto'g'ri (xavfli — SQL injection): `f"... WHERE id = {x}"`.
2. Parametrlar har doim **tuple**: bitta qiymat uchun ham `(5,)` (vergul bilan).
3. **`fetchall()`** — hamma qator, **`fetchone()`** — bitta qator.
4. INSERT/UPDATE/DELETE'dan keyin **`conn.commit()`**; xato bo'lsa
   **`conn.rollback()`** bilan orqaga qaytarish.

`RealDictCursor` ishlatilsa, qator dict bo'lib keladi: `row["full_name"]`.

---

## 6. SQLAlchemy asoslari (ORM)

SQLAlchemy'da jadvalni Python klassi (model) sifatida yozasiz. SQL o'rniga
obyektlar bilan ishlaysiz, `relationship()` esa JOIN'ni avtomatlashtiradi.

```python
class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String)
    orders: Mapped[list["Order"]] = relationship(back_populates="customer")
```

`relationship()` sehri — bir mijozning buyurtmalarini JOIN yozmasdan olasiz:

```python
customer = session.get(Customer, 1)
for order in customer.orders:     # SQLAlchemy o'zi JOIN qiladi
    print(order.id)
```

Aniq JOIN kerak bo'lsa (agregatsiya bilan):

```python
session.query(Customer.full_name, func.sum(...))\
       .join(Order, Order.customer_id == Customer.id)\      # INNER JOIN
       .outerjoin(OrderItem, ...)\                          # LEFT JOIN
       .group_by(Customer.id)
```

---

## 7. psycopg2 yoki SQLAlchemy — qaysi biri?

| | psycopg2 | SQLAlchemy |
|---|----------|------------|
| Yondashuv | Sof SQL yozasiz | Model/obyekt bilan |
| Nazorat | To'liq, har bir so'rov qo'lda | Ko'pini o'zi qiladi |
| Qachon qulay | Murakkab, optimallashtirilgan so'rovlar; kichik skriptlar | Katta ilovalar, ko'p jadval, CRUD ko'p |
| O'rganish | SQL bilsangiz — oson | Biroz ko'proq tushuncha kerak |

Amalda: **SQL'ni yaxshi tushunish uchun avval psycopg2 bilan mashq qiling**,
keyin katta loyihalarda SQLAlchemy'ga o'ting. SQLAlchemy ichida ham baribir
psycopg2 ishlaydi (`postgresql+psycopg2://...`).

---

## 8. Keyingi qadam

`MASHQLAR.md` faylini oching — u yerda 8 ta mashq bor. Avval o'zingiz
yozib ko'ring, keyin yechim bilan solishtiring. `03_queries.sql`dagi
tayyor so'rovlarni ham `psql -d dokon -f 03_queries.sql` bilan ishga
tushirib, natijalarni kuzating.
