# Mashqlar — JOIN va relationship

Avval **o'zingiz** `psql -d dokon` ichida yozib ko'ring. Keyin yechim bilan
solishtiring. Yechimlar oxirida (bo'lim 2). Har bir yechim haqiqiy bazada
tekshirilgan.

## Savollar

1. **(Oson)** Faqat Toshkentdagi mijozlarning ism va emailini chiqaring.

2. **(INNER JOIN)** Har bir buyurtmani mijoz ismi bilan ko'rsating:
   `order_id`, `full_name`, `status`.

3. **(JOIN + GROUP BY)** Har bir buyurtmaning umumiy summasini hisoblang
   (`order_items` bo'yicha `quantity * unit_price` yig'indisi). Faqat
   `status = 'paid'` bo'lganlarini oling.

4. **(LEFT JOIN + IS NULL)** Umuman buyurtma qilmagan mijozlarni toping.

5. **(JOIN + agregatsiya)** Har bir mahsulot necha marta buyurtmada uchragan
   (`nechta_satr`) va jami necha dona sotilgan (`jami_dona`)? Ko'p sotilgani
   birinchi bo'lsin.

6. **(JOIN + ORDER BY + LIMIT)** Eng katta summali bitta buyurtmani toping
   (mijoz ismi va summasi bilan).

7. **(Ko'p jadval + GROUP BY)** Har bir shahar bo'yicha: nechta mijoz bor va
   o'sha shahar mijozlarining jami xaridi qancha (bekor qilingan buyurtmalarni
   hisobga olmang).

8. **(JOIN + sana filtri)** 2026-yil aprel oyida (`order_date`) buyurtma
   qilgan mijozlarning ismlarini takrorlanmasdan chiqaring.

---

## Yechimlar

### 1
```sql
SELECT full_name, email
FROM customers
WHERE city = 'Toshkent';
```

### 2
```sql
SELECT o.id AS order_id, c.full_name, o.status
FROM orders o
JOIN customers c ON c.id = o.customer_id
ORDER BY o.id;
```

### 3
```sql
SELECT o.id AS order_id,
       SUM(oi.quantity * oi.unit_price) AS jami
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.status = 'paid'
GROUP BY o.id
ORDER BY o.id;
```

### 4
```sql
SELECT c.full_name, c.city
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;
```

### 5
```sql
SELECT p.name,
       COUNT(oi.id)       AS nechta_satr,
       SUM(oi.quantity)   AS jami_dona
FROM products p
JOIN order_items oi ON oi.product_id = p.id
GROUP BY p.id, p.name
ORDER BY jami_dona DESC;
```

### 6
```sql
SELECT c.full_name,
       SUM(oi.quantity * oi.unit_price) AS jami
FROM orders o
JOIN customers   c  ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id, c.full_name
ORDER BY jami DESC
LIMIT 1;
```

### 7
```sql
SELECT c.city,
       COUNT(DISTINCT c.id) AS mijozlar_soni,
       COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS jami_xarid
FROM customers c
LEFT JOIN orders      o  ON o.customer_id = c.id AND o.status <> 'cancelled'
LEFT JOIN order_items oi ON oi.order_id   = o.id
GROUP BY c.city
ORDER BY jami_xarid DESC;
```

### 8
```sql
SELECT DISTINCT c.full_name
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.order_date >= '2026-04-01'
  AND o.order_date <  '2026-05-01'
ORDER BY c.full_name;
```

---

> **Maslahat:** har bir yechimni psycopg2 yoki SQLAlchemy'da ham qayta yozib
> ko'ring. Masalan 4-mashqni SQLAlchemy'da: `.outerjoin(Order, ...)` + filtrda
> `Order.id.is_(None)`.
