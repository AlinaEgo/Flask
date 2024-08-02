import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Integer, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

load_dotenv()

POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '123456')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'flask_app')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5431')

engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
                       f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Advertisement(Base):
    __tablename__ = 'advertisement'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    owner: Mapped[str] = mapped_column(String, nullable=False)
    creation_date: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())


    def dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'owner': self.owner,
            'creation_date': self.creation_date.isoformat(),
        }


Base.metadata.create_all(bind=engine)