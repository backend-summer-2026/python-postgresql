-- ============================================================
--  JOIN va relationship so'rovlari (namunalar)
--  Har bir so'rovni psql'da alohida ishga tushirib ko'ring.
-- ============================================================

-- (1) INNER JOIN — har bir buyurtma qaysi mijozniki
--     Faqat mos keladigan qatorlar chiqadi.
SELECT o.id AS order_id, c.full_name, o.order_date, o.status
FROM orders o
JOIN customers c ON c.id = o.customer_id
ORDER BY o.id;

-- (2) 3 ta jadvalni bog'lash — buyurtma ichidagi mahsulotlar
SELECT o.id AS order_id,
       c.full_name,
       p.name  AS product,
       oi.quantity,
       oi.unit_price,
       (oi.quantity * oi.unit_price) AS satr_summasi
FROM orders o
JOIN customers   c  ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
JOIN products    p  ON p.id = oi.product_id
ORDER BY o.id, p.name;

-- (3) LEFT JOIN — buyurtma qilmagan mijozlarni ham ko'rsatish
--     Gulnora'da buyurtma yo'q => order_id NULL bo'lib chiqadi.
SELECT c.full_name, o.id AS order_id
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
ORDER BY c.full_name;

-- (4) LEFT JOIN + IS NULL — "hech qachon buyurtma qilmagan" mijozlar
SELECT c.full_name, c.city
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;

-- (5) JOIN + GROUP BY — har bir mijozning nechta buyurtmasi bor
SELECT c.full_name, COUNT(o.id) AS buyurtmalar_soni
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.full_name
ORDER BY buyurtmalar_soni DESC, c.full_name;

-- (6) JOIN + agregatsiya — har bir buyurtmaning umumiy summasi
SELECT o.id AS order_id, c.full_name,
       SUM(oi.quantity * oi.unit_price) AS jami
FROM orders o
JOIN customers   c  ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id, c.full_name
ORDER BY jami DESC;

-- (7) Eng ko'p sotilgan mahsulotlar (dona bo'yicha)
SELECT p.name, SUM(oi.quantity) AS jami_dona
FROM products p
JOIN order_items oi ON oi.product_id = p.id
GROUP BY p.id, p.name
ORDER BY jami_dona DESC;

-- (8) Hech sotilmagan mahsulotlar (LEFT JOIN + IS NULL)
SELECT p.name, p.category
FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.id
WHERE oi.id IS NULL;

-- (9) Har bir mijozning jami xarid summasi (faqat bekor qilinmagan buyurtmalar)
SELECT c.full_name,
       COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS jami_xarid
FROM customers c
LEFT JOIN orders      o  ON o.customer_id = c.id AND o.status <> 'cancelled'
LEFT JOIN order_items oi ON oi.order_id   = o.id
GROUP BY c.id, c.full_name
ORDER BY jami_xarid DESC;

-- (10) HAVING — 500 000 so'mdan ko'p xarid qilgan mijozlar
SELECT c.full_name, SUM(oi.quantity * oi.unit_price) AS jami
FROM customers c
JOIN orders      o  ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id   = o.id
GROUP BY c.id, c.full_name
HAVING SUM(oi.quantity * oi.unit_price) > 500000
ORDER BY jami DESC;
