from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Numeric
from app.models.strategy_model import Strategy
from app.models.investment_profile_model import InvestmentProfile
from sqlalchemy.types import Enum
import enum

Base = declarative_base()

class OperationTypeEnum(enum.Enum):
    Buy = 'Buy'
    Sell = 'Sell'

class PeriodEnum(enum.Enum):
    period_1 = 'Period 1'
    period_2 = 'Period 2'
    period_3 = 'Period 3'

class Operation(Base):
  __tablename__ = 'operation'
  
  id = Column(Integer, primary_key=True)
  asset = Column(String(100), nullable=False)
  operation_date = Column(DateTime, nullable=False)
  operation_type = Column(Enum(OperationTypeEnum, name='operation_type'), nullable=False)
  amount = Column(Numeric(15, 2), nullable=False)
  unit_price = Column(Numeric(15, 2), nullable=False)
  total_return = Column(Numeric(15, 2), nullable=False)
  period = Column(Enum('Period 1', 'Period 2', 'Period 3', name='period'), nullable=False)
  
  investment_profile_id = Column(Integer, nullable=False)
  strategy_id = Column(Integer, nullable=False)