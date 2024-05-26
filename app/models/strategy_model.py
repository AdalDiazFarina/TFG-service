from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Strategy(Base):
    __tablename__ = 'strategy'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    model = Column(String)
