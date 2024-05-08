from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.models.user_model import User
from app.models.strategy_model import Strategy
from app.models.investment_profile_model import InvestmentProfile
from app.models.investment_profile_strategy_model import InvestmentProfileStrategy

# Crear un objeto Session de SQLAlchemy
engine = create_engine("postgresql://root:1234@localhost:5432/FundFlowForge")
Session = sessionmaker(bind=engine)

def create_strategy_record(strategy_name, strategy_description):
    session = Session()
    try:
        # Comprobar si la estrategia ya existe
        existing_strategy = session.query(Strategy).filter_by(name=strategy_name).first()
        if existing_strategy:
            print("Strategy with the name '{}' already exists.".format(strategy_name))
        else:
            new_strategy = Strategy(
                name=strategy_name,
                description=strategy_description
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
                    )
                    session.add(new_entry)

        session.commit()
        print("### Successfully associated strategies with profiles.")
    except SQLAlchemyError as error:
        print("&&&& Error associating strategies with profiles:", error)
        session.rollback()
    finally:
        session.close()
