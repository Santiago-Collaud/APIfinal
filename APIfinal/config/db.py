from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("postgresql://postgres:santicoll@localhost:5432/APIfinal", echo=True)

Base = declarative_base()