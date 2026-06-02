from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Строка подключения к PostgreSQL. 
# Замени 'postgres', 'password' и 'toy_shop' на свои актуальные данные из pgAdmin:
# postgres://ПОЛЬЗОВАТЕЛЬ:ПАРОЛЬ@localhost:ПОРТ/ИМЯ_БАЗЫ_ДАННЫХ
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost:5432/toy_shop"

# Создаем движок SQLAlchemy. 
# В отличие от SQLite, для PostgreSQL никаких дополнительных аргументов типа check_same_thread передавать не нужно.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Настраиваем фабрику сессий для работы с транзакциями
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Функция для получения сессии БД.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()