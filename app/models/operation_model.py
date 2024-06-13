from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Date, Numeric, ForeignKey
from app.models.strategy_model import Strategy
from app.models.investment_profile_model import InvestmentProfile

Base = declarative_base()

class Operation(Base):
  __tablename__ = 'operation'
  
  id = Column(Integer, primary_key=True)
  id_strategy = Column(Integer, ForeignKey(Strategy.id, ondelete='CASCADE'))
  id_profile = Column(Integer, ForeignKey(InvestmentProfile.id, ondelete='CASCADE'))
  total = Column(Numeric)
  profit = Column(Numeric)
  period = Column(String)
  start_date = Column(Date)
  end_date = Column(Date)