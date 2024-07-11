from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.user_model import User

Base = declarative_base()

class InvestmentProfile(Base):
    __tablename__ = 'investment_profile'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    name = Column(String(255))
    description = Column(String(255))
    initial_capital = Column(Numeric)
    duration = Column(Numeric)
    monthly_contribution = Column(Numeric)
