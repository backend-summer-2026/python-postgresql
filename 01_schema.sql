-- ============================================================
--  ONLAYN DO'KON — sxema (jadvallar va relationship'lar)
-- ============================================================
--  Relationship'lar (bog'lanishlar):
--
--   customers (mijozlar)  1 ──────< orders (buyurtmalar)
--                                      │  1
--                                      │
--                                      ˅  ko'p (many)
--   products (mahsulotlar) 1 ──────< order_items (buyurtma satrlari)
--
--   • Bitta mijozda ko'p buyurtma bo'ladi        -> one-to-many
--   • Bitta buyurtmada ko'p satr (mahsulot) bor  -> one-to-many
--   • Bitta mahsulot ko'p satrlarda uchraydi     -> one-to-many
--   • orders <-> products aslida MANY-TO-MANY,
--     order_items — ular orasidagi "bog'lovchi" (junction) jadval.
-- ============================================================

DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders      CASCADE;
DROP TABLE IF EXISTS products    CASCADE;
DROP TABLE IF EXISTS customers   CASCADE;

-- 1) Mijozlar
CREATE TABLE customers (
    id          SERIAL PRIMARY KEY,
    full_name   TEXT        NOT NULL,
    city        TEXT        NOT NULL,
    email       TEXT        UNIQUE NOT NULL,
    created_at  DATE        NOT NULL DEFAULT CURRENT_DATE
);

-- 2) Mahsulotlar
CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        TEXT           NOT NULL,
    category    TEXT           NOT NULL,
    price       NUMERIC(10,2)  NOT NULL CHECK (price >= 0), -- 12345678.90
    stock       INT            NOT NULL DEFAULT 0
);

-- 3) Buyurtmalar  (har biri bitta mijozga tegishli)
CREATE TABLE orders (
    id           SERIAL PRIMARY KEY,
    customer_id  INT   NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    order_date   DATE  NOT NULL DEFAULT CURRENT_DATE,
    status       TEXT  NOT NULL DEFAULT 'new'   -- new / paid / shipped / cancelled
);

-- 4) Buyurtma satrlari (junction: qaysi buyurtmada qaysi mahsulot, nechta)
CREATE TABLE order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INT NOT NULL REFERENCES orders(id)   ON DELETE CASCADE,
    product_id  INT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity    INT NOT NULL CHECK (quantity > 0),
    unit_price  NUMERIC(10,2) NOT NULL   -- sotib olingan paytdagi narx
);

-- Tez-tez ishlatiladigan foreign key'larga indeks (yaxshi amaliyot)
CREATE INDEX idx_orders_customer   ON orders(customer_id);
CREATE INDEX idx_items_order       ON order_items(order_id);
CREATE INDEX idx_items_product     ON order_items(product_id);
