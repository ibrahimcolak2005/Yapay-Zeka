from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite için gerekli
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Tüm modellerin miras alacağı temel sınıf."""
    pass


def get_db():
    """Her istek için bir veritabanı oturumu oluşturur ve istek bitince kapatır."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
