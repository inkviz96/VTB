from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db = "postgresql+psycopg2://vtb:vtb@db:5432/vtb"
db_engine = create_engine(db)

Session = sessionmaker(db_engine)
session = Session()
