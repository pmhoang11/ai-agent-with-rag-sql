from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL
)

Session = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False
)


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()