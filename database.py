import atexit
from sqlalchemy import Column, String, Integer, create_engine, Numeric
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base
from decouple import config

PG_DSN = f'postgresql://{config("DB_USER")}:{config("DB_PASSWORD")}@127.0.0.1:5432/{config("DB_NAME")}'
engine = create_engine(PG_DSN)

Base = declarative_base()
Session = create_session(bind=engine, autocommit=False)

atexit.register(engine.dispose)
class Parts(Base):
    __tablename__ = 'parts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Numeric, nullable=True)

    def __str__(self):
        return self.code

Base.metadata.create_all(bind=engine)