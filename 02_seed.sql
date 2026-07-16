-- ============================================================
--  Namunaviy ma'lumotlar (seed data)
-- ============================================================

-- Mijozlar
INSERT INTO customers (full_name, city, email, created_at) VALUES
  ('Ali Valiyev',      'Toshkent',   'ali@mail.uz',    '2026-01-05'),
  ('Nodira Karimova',  'Samarqand',  'nodira@mail.uz', '2026-01-10'),
  ('Bekzod Toshmatov', 'Toshkent',   'bekzod@mail.uz', '2026-02-01'),
  ('Malika Yusupova',  'Buxoro',     'malika@mail.uz', '2026-02-14'),
  ('Sardor Rasulov',   'Samarqand',  'sardor@mail.uz', '2026-03-02');
  -- (Diqqat: keyingi mijoz "Gulnora" ataylab buyurtmasiz qoldirildi — LEFT JOIN mashqi uchun)
INSERT INTO customers (full_name, city, email, created_at) VALUES
  ('Gulnora Ahmedova', 'Xorazm',     'gulnora@mail.uz', '2026-03-20');

-- Mahsulotlar
INSERT INTO products (name, category, price, stock) VALUES
  ('Noutbuk Lenovo',   'Elektronika', 7200000.00, 12),
  ('Simsiz sichqoncha','Elektronika',  120000.00, 80),
  ('Mexanik klaviatura','Elektronika', 450000.00, 30),
  ('Qahva doni 1kg',   'Oziq-ovqat',    95000.00, 200),
  ('Termokружка',      'Uy-ro''zg''or', 85000.00,  50),
  ('Blaknot A5',       'Kanstovar',     18000.00, 300),
  ('USB kabel',        'Elektronika',   35000.00, 150),
  ('Simsiz quloqchin', 'Elektronika',  340000.00,  25);
  -- ("Simsiz quloqchin" ataylab hech sotilmagan — LEFT JOIN + IS NULL mashqi uchun)

-- Buyurtmalar
INSERT INTO orders (customer_id, order_date, status) VALUES
  (1, '2026-03-01', 'paid'),      -- 1: Ali
  (1, '2026-04-15', 'shipped'),   -- 2: Ali
  (2, '2026-03-05', 'paid'),      -- 3: Nodira
  (3, '2026-04-02', 'new'),       -- 4: Bekzod
  (4, '2026-04-20', 'cancelled'), -- 5: Malika
  (2, '2026-05-10', 'paid');      -- 6: Nodira

-- Buyurtma satrlari (order_id, product_id, quantity, unit_price)
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
  (1, 1, 1, 7200000.00),   -- Ali: 1 noutbuk
  (1, 2, 2,  120000.00),   -- Ali: 2 sichqoncha
  (2, 4, 3,   95000.00),   -- Ali: 3 qahva
  (2, 6, 5,   18000.00),   -- Ali: 5 blaknot
  (3, 3, 1,  450000.00),   -- Nodira: 1 klaviatura
  (3, 2, 1,  120000.00),   -- Nodira: 1 sichqoncha
  (4, 7, 4,   35000.00),   -- Bekzod: 4 USB kabel
  (5, 1, 1, 7200000.00),   -- Malika: 1 noutbuk (bekor qilingan)
  (6, 5, 2,   85000.00),   -- Nodira: 2 termokружка
  (6, 4, 1,   95000.00);   -- Nodira: 1 qahva
