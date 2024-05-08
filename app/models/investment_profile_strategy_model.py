from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Numeric, ForeignKey
from app.models.investment_profile_model import InvestmentProfile
from app.models.strategy_model import Strategy

Base = declarative_base()

class InvestmentProfileStrategy(Base):
    __tablename__ = 'investment_profile_strategy'

    investment_profile_id = Column(Integer, ForeignKey(InvestmentProfile.id), primary_key=True)
    strategy_id = Column(Integer, ForeignKey(Strategy.id), primary_key=True)
    total_profitability = Column(Numeric)
    volatility = Column(Numeric)
    maximum_loss = Column(Numeric)
    sharpe = Column(Numeric)
    sortino = Column(Numeric)
    alpha = Column(Numeric)
    beta = Column(Numeric)
    information_ratio = Column(Numeric)
    success_rate = Column(Numeric)
    portfolio_concentration_ratio = Column(Numeric)