# ------- Синхронное подключение к SQLite -------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import PASSWORD_FOR_DB

# Строка подключения для SQLite
DATABASE_URL = "sqlite:///../ecommerce.db"

# Создание Engine
engine = create_engine(DATABASE_URL, echo=True)

# Настройка фабрики сеансов
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

# ------- Асинхронное подключение к PostgreSQL -------

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Строка подключения для PostgreSQL
DATABASE_URL = f"postgresql+asyncpg://ecommerce_user:{PASSWORD_FOR_DB}@localhost:5432/ecommerce_db"

# Создаем Engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Настройка фабрики сеансов
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass