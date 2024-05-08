from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey
from app.models.strategy_model import Strategy

Base = declarative_base()

class Operation(Base):
  __tablename__ = 'operation'
  
  id = Column(Integer, primary_key=True)
  id_strategy = Column(Integer, ForeignKey(Strategy.id, ondelete='CASCADE'))
  profit = Column(Numeric)
  start_date = Column(Date)
  end_date = Column(Date)