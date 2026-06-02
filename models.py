from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, CheckConstraint, Numeric, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base # Предполагается, что Base импортируется из файла настроек БД

# =====================================================================
# ТАБЛИЦЫ-СПРАВОЧНИКИ (Для соблюдения 3-й нормальной формы)
# =====================================================================

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # client, manager, admin

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class Manufacturer(Base):
    __tablename__ = "manufacturers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class Unit(Base):
    __tablename__ = "units"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # шт., кг., упак.

# =====================================================================
# ОСНОВНЫЕ СУЩНОСТИ: ПОЛЬЗОВАТЕЛИ И ТОВАРЫ
# =====================================================================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True) # Логин
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False) # ФИО пользователя для правого верхнего угла
    
    # Внешний ключ на роль
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Внешние ключи на справочники (3НФ)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id", ondelete="RESTRICT"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id", ondelete="RESTRICT"), nullable=False)
    
    # Ограничения (CheckConstraints) согласно ТЗ: не отрицательные цена и остаток
    price = Column(Numeric(10, 2), nullable=False) # Сотые части поддерживаются
    discount = Column(Integer, default=0, nullable=False) # Процент скидки (0-100)
    stock_quantity = Column(Integer, nullable=False, default=0)
    
    # Картинка заглушка по умолчанию, если фото не загружено
    image_path = Column(String, default="picture.png")
    
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
        CheckConstraint('stock_quantity >= 0', name='check_stock_positive'),
    )

    # Связи для ORM
    category = relationship("Category")
    manufacturer = relationship("Manufacturer")
    supplier = relationship("Supplier")
    unit = relationship("Unit")

# =====================================================================
# ЗАКАЗЫ (Связь Многие-ко-Многим между Товарами и Заказами)
# =====================================================================

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="Новый") # Статус заказа
    
    user = relationship("User")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    
    # КРИТИЧНО ДЛЯ ТЗ: ondelete="RESTRICT" запрещает удалять товар, если он есть в заказе
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Numeric(10, 2), nullable=False) # Фиксируем цену на момент покупки (с учетом скидки)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")