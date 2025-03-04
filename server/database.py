from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

class DatabaseManager:
    def __init__(self, db_url='sqlite:///myapp2.db'):
        self.engine = create_engine(db_url, echo=True)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Возвращает новую сессию для работы с базой данных."""
        return self.Session()

    def session_scope(self):
        """Контекстный менеджер для автоматического управления сессиями."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()