from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.models.user_model import User
from app.models.strategy_model import Strategy
from app.models.investment_profile_model import InvestmentProfile
from app.models.investment_profile_strategy_model import InvestmentProfileStrategy
from app.models.operation_model import Operation
import json

# Crear un objeto Session de SQLAlchemy
engine = create_engine("postgresql://root:1234@localhost:5432/FundFlowForge")
Session = sessionmaker(bind=engine)

def create_strategy_record(strategy_name, strategy_description, strategy_model):
    session = Session()
    try:
        # Comprobar si la estrategia ya existe
        existing_strategy = session.query(Strategy).filter_by(name=strategy_name).first()
        if existing_strategy:
            print("Strategy with the name '{}' already exists.".format(strategy_name))
        else:
            new_strategy = Strategy(
                name=strategy_name,
                description=strategy_description,
                model=strategy_model
            )
            session.add(new_strategy)
            session.commit()
            print("### Strategy record created successfully. ###\n")
    except SQLAlchemyError as error:
        print("&&&& Error creating strategy record: ", error)
        session.rollback()
    finally:
        session.close()

def associate_strategies_with_profiles():
    session = Session()
    
    try:
        strategies = session.query(Strategy).all()
        profiles = session.query(InvestmentProfile).all()

        for strategy in strategies:
            for profile in profiles:
                # Comprobar si la asociación ya existe
                existing_association = session.query(InvestmentProfileStrategy).filter_by(
                    investment_profile_id=profile.id,
                    strategy_id=strategy.id
                ).first()
                if existing_association:
                    print("- Association between Strategy '{}' and Profile '{}' already exists.".format(
                        strategy.name, profile.name))
                else:
                    new_entry = InvestmentProfileStrategy(
                        investment_profile_id=profile.id,
                        strategy_id=strategy.id,
                        validated=False,
                        total_profitability=0.0,
                        volatility=0.0,
                        maximum_loss=0.0,
                        sharpe=0.0,
                        sortino=0.0,
                        alpha=0.0,
                        beta=0.0,
                        information_ratio=0.0,
                        success_rate=0.0,
                        portfolio_concentration_ratio=0.0,
                        annual_return=0.0,
                    )
                    session.add(new_entry)

        session.commit()
        print("### Successfully associated strategies with profiles.")
    except SQLAlchemyError as error:
        print("&&&& Error associating strategies with profiles:", error)
        session.rollback()
    finally:
        session.close()

def updateInvestmentProfileStrategy(profile_id, strategy_id, data):
    session = Session()
    try:
        existing_association = session.query(InvestmentProfileStrategy).filter_by(
            investment_profile_id=profile_id,
            strategy_id=strategy_id
        ).first()
        if existing_association:
            existing_association.validated = True
            existing_association.total_profitability = data[0]['total_profitability']
            existing_association.volatility = data[0]['volatility']
            existing_association.maximum_loss = data[0]['maximum_loss']
            existing_association.sharpe = data[0]['sharpe']
            existing_association.sortino = data[0]['sortino']
            existing_association.alpha = data[0]['alpha']
            existing_association.beta = data[0]['beta']
            existing_association.information_ratio = data[0]['information_ratio']
            existing_association.success_rate = data[0]['success_rate']
            existing_association.portfolio_concentration_ratio = data[0]['portfolio_concentration_ratio']
            existing_association.annual_return = data[0]['annual_return']
            
        session.commit()

        print("### Successfully associated strategies with profiles.")
    except SQLAlchemyError as error:
        print("&&&& Error associating strategies with profiles:", error)
        session.rollback()
    finally:
        session.close()

def create_operations(profile_id, strategy_id, data):
    session = Session()
    operations_to_delete = session.query(Operation).filter_by(
        investment_profile_id=profile_id,
        strategy_id=strategy_id
    ).all()

    for operation in operations_to_delete:
        session.delete(operation)

    session.commit()

    for i in range(len(data)):
       new_entry = Operation(
        operation_type=data[i]["operation_type"],
        asset=data[i]["asset"],
        operation_date=data[i]["operation_date"],
        amount=data[i]["amount"],
        unit_price=data[i]["unit_price"],
        total_return=data[i]["total_return"],
        investment_profile_id=profile_id,
        strategy_id=strategy_id,
        period=data[i]["period"]
       )

       session.add(new_entry)

    session.commit()

def getModelName(id):
    session = Session()
    return session.query(Strategy).get(id).model