from sqlalchemy.orm import Session
from collections.abc import Generator

from app.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных.
    Создает новую сессию для каждого запроса и закрывает её после обработки.
    :return:
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()