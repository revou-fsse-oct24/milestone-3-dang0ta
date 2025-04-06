from typing import Optional, List
from models import CreateBudgetRequest, UpdateBudgetRequest, Budget as BudgetModel, UserInformation
from .db import Budgets, db_session, Users
from db.users import UserNotFoundException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

class BudgetsNotFoundException(Exception):
    def __init__(self, user_id:str):
        super().__init__("no budgets available for the user")
        self.user_id = user_id

class BudgetNotFoundException(Exception):
    def __init__(self, budget_id: str):
        super().__init__("budget can't be found")
        self.budget_id = budget_id

def create_budget(user_id: str, request: CreateBudgetRequest) -> Optional[BudgetModel]:
    user = db_session.get(Users, user_id)
    if user is None:
        raise UserNotFoundException(user_id = user_id)
    
    budget = Budgets(
        name=request.name,
        user_id=user_id,
        amount=request.amount,
        start_date=request.start_date,
        end_date=request.end_date,
    )

    db_session.add(budget)
    db_session.flush()

    response = BudgetModel(
        id=str(budget.id),
        name=budget.name,
        user=UserInformation(
            name=user.username,
            fullname=user.fullname,
            email_address=user.email,
            default_account=None,
            roles=user.roles.split(","),     
        ),
        amount=budget.amount,
        start_date=budget.start_date.isoformat(),
        end_date=budget.end_date.isoformat(),
    )

    db_session.commit()
    return response
    
def get_budgets(user_id: str) -> List[BudgetModel]:
    try:
        statement = select(Budgets).where(Budgets.user_id.is_(user_id))
        budgets = db_session.scalars(statement=statement).all()
        return [BudgetModel(
            id=str(budget.id),
            name=budget.name,
            amount=budget.amount,
            start_date=budget.start_date.isoformat(),
            end_date=budget.end_date.isoformat(),
        ) for budget in budgets]
    except NoResultFound as e:
        db_session.rollback()
        raise BudgetsNotFoundException(user_id=user_id)
    
def update_budget(budget_id: str, request: UpdateBudgetRequest)-> Optional[BudgetModel]:
    try:
        budget = db_session.get(Budgets, budget_id)
        if request.amount is not None:
            budget.amount = request.amount
        if request.name is not None:
            budget.name = request.name
        if request.start_date is not None:
            budget.start_date = request.start_date
        if request.end_date is not None:
            budget.end_date = request.end_date

        db_session.flush()
        db_session.commit()
    except NoResultFound:
        db_session.rollback()
        raise BudgetNotFoundException(budget_id=budget_id)
    
def delete_budget(budget_id:str):
    try:
        budget = db_session.get(Budgets, budget_id)
        db_session.delete(budget)
        db_session.flush()
        db_session.commit()
    except NoResultFound:
        db_session.rollback()
        raise BudgetNotFoundException(budget_id=budget_id)