from sqlalchemy import Column, VARCHAR, Integer, BOOLEAN, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Dataset(Base):
    __tablename__ = 'dataset'

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    status = Column(VARCHAR(255), nullable=False)
    data = Column(JSON, nullable=False)
    sell = Column(BOOLEAN, nullable=False)
    price = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    mail = Column(VARCHAR(255), nullable=False)


class Bill(Base):
    __tablename__ = 'bill'

    id = Column(Integer, primary_key=True)
    receipt = Column(VARCHAR(255), nullable=False)
    dataset_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
