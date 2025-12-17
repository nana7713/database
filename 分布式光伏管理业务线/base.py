from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager


class DatabaseManager:
    def __init__(self, database_url, **engine_kwargs):

        self.engine = create_engine(database_url, **engine_kwargs)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        self.Base = declarative_base()

    @contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def close_connection(self):
        self.engine.dispose()


DATABASE_URL = "mysql+pymysql://root:yy20041008@localhost/smart_energy?charset=utf8"
db_manager = DatabaseManager(
    DATABASE_URL,
    pool_size=10,
    max_overflow=5,
)
