"""
============================================================
 ONLAYN DO'KON — SQLAlchemy (ORM) bilan ishlash (amaliy)
============================================================
Bir xil bazaning ustida, lekin endi SQL yozish o'rniga Python
klasslari (model'lar) bilan ishlaymiz. relationship() bog'lanishlarni
avtomatik JOIN'ga aylantiradi.

Ishga tushirishdan oldin:
  1) pip install sqlalchemy psycopg2-binary
  2) Baza tayyor bo'lsin (01_schema.sql, 02_seed.sql yuklangan).
  3) DB_URL'ni o'zingiznikiga moslang.
  4) python app_sqlalchemy.py

Eslatma: bu skript mavjud jadvallarni O'ZI YARATMAYDI (SQL fayldan
foydalanadi), shunchaki ularga model orqali murojaat qiladi.
"""

from datetime import date
from decimal import Decimal
from sqlalchemy import (
    create_engine, String, Integer, Numeric, Date, ForeignKey, func
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, Session
)

# postgresql+psycopg2://foydalanuvchi:parol@host:port/baza
DB_URL = "postgresql+psycopg2://djumanov:Djcjder1120@localhost:5432/dokon_db"
engine = create_engine(DB_URL, echo=False)   # echo=True qilsangiz SQL'ni ko'rasiz


# ------------------------------------------------------------
#  Model'lar — har bir klass bitta jadvalga mos keladi
# ------------------------------------------------------------
class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"
    id:        Mapped[int]  = mapped_column(primary_key=True)
    full_name: Mapped[str]  = mapped_column(String)
    city:      Mapped[str]  = mapped_column(String)
    email:     Mapped[str]  = mapped_column(String)

    # 1 mijoz -> ko'p buyurtma. back_populates ikki tomonni bog'laydi.
    orders: Mapped[list["Order"]] = relationship(back_populates="customer")


class Product(Base):
    __tablename__ = "products"
    id:       Mapped[int]   = mapped_column(primary_key=True)
    name:     Mapped[str]   = mapped_column(String)
    category: Mapped[str]   = mapped_column(String)
    price:    Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock:    Mapped[int]   = mapped_column(Integer)

    items: Mapped[list["OrderItem"]] = relationship(back_populates="product")


class Order(Base):
    __tablename__ = "orders"
    id:          Mapped[int]  = mapped_column(primary_key=True)
    customer_id: Mapped[int]  = mapped_column(ForeignKey("customers.id"))
    order_date:  Mapped[date] = mapped_column(Date)
    status:      Mapped[str]  = mapped_column(String)

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    items:    Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    id:         Mapped[int]   = mapped_column(primary_key=True)
    order_id:   Mapped[int]   = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int]   = mapped_column(ForeignKey("products.id"))
    quantity:   Mapped[int]     = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order:   Mapped["Order"]   = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="items")


# ------------------------------------------------------------
# 1) relationship orqali "avtomatik JOIN" — SQL yozmasdan
# ------------------------------------------------------------
def buyurtmalarni_korish():
    with Session(engine) as session:
        # Barcha buyurtmalarni olamiz; .customer va .items o'zi yuklanadi
        orders = session.query(Order).order_by(Order.id).all()
        print("\n== Buyurtmalar (relationship orqali) ==")
        for o in orders:
            print(f"  #{o.id} | {o.customer.full_name} | {o.status}")
            for it in o.items:
                print(f"       - {it.product.name}: {it.quantity} x {it.unit_price}")


# ------------------------------------------------------------
# 2) Aniq JOIN + agregatsiya: mijoz bo'yicha jami xarid
# ------------------------------------------------------------
def mijoz_boyicha_jami():
    with Session(engine) as session:
        rows = (
            session.query(
                Customer.full_name,
                func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0)
                    .label("jami"),
            )
            .outerjoin(Order, Order.customer_id == Customer.id)   # LEFT JOIN
            .outerjoin(OrderItem, OrderItem.order_id == Order.id)
            .group_by(Customer.id, Customer.full_name)
            .order_by(func.coalesce(
                func.sum(OrderItem.quantity * OrderItem.unit_price), 0).desc())
        )
        print("\n== Mijoz bo'yicha jami xarid (LEFT JOIN + GROUP BY) ==")
        for full_name, jami in rows:
            print(f"  {full_name:<18} | {jami}")


# ------------------------------------------------------------
# 3) Filtrlangan JOIN: eng ko'p sotilgan mahsulotlar
# ------------------------------------------------------------
def top_mahsulotlar(limit: int = 3):
    with Session(engine) as session:
        rows = (
            session.query(
                Product.name,
                func.sum(OrderItem.quantity).label("jami_dona"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)   # INNER JOIN
            .group_by(Product.id, Product.name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        )
        print(f"\n== TOP {limit} sotilgan mahsulot ==")
        for name, dona in rows:
            print(f"  {name:<20} | {dona} dona")


# ------------------------------------------------------------
# 4) Yozish (ORM) — yangi mijoz qo'shish
# ------------------------------------------------------------
def yangi_mijoz(full_name: str, city: str, email: str):
    with Session(engine) as session:
        yangi = Customer(full_name=full_name, city=city, email=email)
        session.add(yangi)
        session.commit()      # INSERT shu yerda bajariladi
        print(f"\n== Yangi mijoz qo'shildi: {yangi.full_name} (id={yangi.id}) ==")


def main():
    buyurtmalarni_korish()
    mijoz_boyicha_jami()
    top_mahsulotlar()
    # yangi_mijoz("Test Foydalanuvchi", "Toshkent", "test@mail.uz")


if __name__ == "__main__":
    main()
