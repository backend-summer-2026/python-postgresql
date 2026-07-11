# Amaliy ish 1. 1:1 Relationship

## Mavzu

**User va Passport**

Har bir foydalanuvchining faqat bitta pasporti bo'ladi.

### users

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    age INT
);
```

### passports

```sql
CREATE TABLE passports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    passport_number VARCHAR(20) UNIQUE,
    issue_date DATE,
    user_id INT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Bu yerda

```
users
------
1  Ali

passports
----------
AA123456 -> user_id=1
```

`user_id UNIQUE` bo'lgani uchun bitta userga faqat bitta passport bog'lanadi.

---

## Vazifa 1

5 ta user qo'shing.

---

## Vazifa 2

Faqat 3 tasiga passport yarating.

---

## Vazifa 3

4-userga passport qo'shing.

---

## Vazifa 4

2-userning passport raqamini o'zgartiring.

---

## Vazifa 5

1-userning passportini o'chiring.

---

## Vazifa 6

Quyidagilarni yozing.

Passport mavjud userlar

(join ishlatmasdan)

Masalan:

```sql
SELECT *
FROM passports
WHERE user_id = 2;
```

---

# Amaliy ish 2. 1:N Relationship

## Mavzu

Customer va Orders

Bitta customer ko'p order berishi mumkin.

---

### customers

```sql
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100),
    phone VARCHAR(20)
);
```

---

### orders

```sql
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100),
    price DECIMAL(10,2),
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

Relationship

```
Customer
--------
1 Ali

Orders
-------
Laptop
Mouse
Keyboard

customer_id = 1
```

---

# Vazifa 1

5 ta customer yarating.

---

# Vazifa 2

Customerlarga quyidagicha order bering.

```
Ali
    Laptop
    Mouse
    Keyboard

Vali
    Monitor

Hasan
    Phone
    Charger

Olim
    yo'q

Bek
    SSD
```

---

# Vazifa 3

Ali yana bitta order bersin.

```
Flashka
```

---

# Vazifa 4

Valining order narxini o'zgartiring.

---

# Vazifa 5

Hasanning "Phone" orderini o'chiring.

---

# Vazifa 6

JOIN ishlatmasdan

Ali buyurtmalarini chiqaring.

Masalan

```sql
SELECT *
FROM orders
WHERE customer_id = 1;
```

---

# Vazifa 7

Customer id=3 ning barcha orderlarini chiqaring.

```sql
SELECT *
FROM orders
WHERE customer_id = 3;
```

---

# Vazifa 8

Narxi 1000 dan katta orderlarni chiqaring.

```sql
SELECT *
FROM orders
WHERE price > 1000;
```

---

# Vazifa 9

Ali nechta order berganini toping.

```sql
SELECT COUNT(*)
FROM orders
WHERE customer_id = 1;
```

---

# Vazifa 10

Har bir customer uchun:

* jami nechta order
* jami summa

hisoblang (har bir customer uchun alohida so'rov yozishingiz mumkin, JOIN talab qilinmaydi).

Masalan:

```sql
SELECT
    COUNT(*) AS total_orders,
    SUM(price) AS total_price
FROM orders
WHERE customer_id = 1;
```

---

# Qo'shimcha Challenge (JOINsiz)

Quyidagi vazifalarni bajaring:

1. Eng qimmat orderni toping.
2. Eng arzon orderni toping.
3. Jami barcha order summasini hisoblang.
4. 2 ta va undan ko'p order bergan customerlarning `customer_id`larini toping.
5. Passporti mavjud bo'lgan foydalanuvchilar sonini hisoblang.
6. Passport berilmagan foydalanuvchilar sonini hisoblash uchun avval `users` va `passports` jadvalidagi ma'lumotlardan foydalanib mantiqiy yechim ishlab chiqing (JOINsiz yondashuv bilan).

Bu mashqlar orqali siz **Primary Key**, **Foreign Key**, **1:1**, **1:N** munosabatlar, **CRUD** (INSERT, UPDATE, DELETE, SELECT) hamda **COUNT**, **SUM**, **MIN**, **MAX** kabi agregat funksiyalarni amalda mustahkamlaysiz.
