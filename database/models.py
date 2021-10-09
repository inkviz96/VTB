from sqlalchemy import Column, VARCHAR, Integer, BOOLEAN, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Dataset(Base):
    __tablename__ = 'dataset'

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    status = Column(JSON, nullable=False)
    sell = Column(BOOLEAN, nullable=False)
    price = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    mail = Column(VARCHAR(255), nullable=False)
