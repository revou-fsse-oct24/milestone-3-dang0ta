from typing import List
from models import CreateBillRequest, Bill, QueryBillsRequest, UpdateBillRequest
from db import db_session, Bills, Users, Accounts
from db.users import UserNotFoundException
from db.accounts import AccountNotFoundException
from sqlalchemy import select

class BillNotFoundException(Exception):
    def __init__(self, bill_id:str):
        super().__init__("the bill can't be found")
        self.bill_id = bill_id

def create_bill(user_id: str, request: CreateBillRequest) -> Bill:
    user = db_session.get(Users, user_id)
    if user is None:
        raise UserNotFoundException(id=user_id)
    
    account_id = request.account_id
    if account_id is None:
        account_id = user.default_account_id
    else:
        account = db_session.get(Accounts, account_id)
        if account is None:
            raise AccountNotFoundException(account_id=account_id)
        
        account_id = account.id

    bill = Bills(
        user_id=user_id,
        biller_name=request.biller_name,
        due_date=request.due_date,
        amount=request.amount,
        account_id=account_id,
    )

    db_session.add(bill)
    db_session.flush()

    model = Bill(
        id=str(bill.id),
        biller_name=request.biller_name,
        due_date=request.due_date.isoformat(),
        amount=request.amount,
        account_id=str(account_id),
    )

    db_session.commit()
    return model

def get_bills(user_id: str, request:QueryBillsRequest) -> List[Bill]:
    user = db_session.get(Users, user_id)
    if user is None:
        raise UserNotFoundException(id=user_id)
    
    statement = (
        select(Bills)
        .where(Bills.user_id.is_(user_id))
    )

    if request.account_id is not None:
        statement = statement.filter(Bills.account_id.is_(request.account_id))
    if request.biller_name is not None:
        statement = statement.filter(Bills.biller_name.like(request.biller_name))
    if request.due_date_from is not None:
        statement = statement.filter(Bills.due_date >= request.due_date_from)
    if request.due_date_to is not None:
        statement = statement.filter(Bills.due_date <= request.due_date_to)
    if request.amount_min is not None:
        statement = statement.filter(Bills.amount >= request.amount_min)
    if request.amount_max is not None:
        statement = statement.filter(Bills.amount <= request.amount_max)

    result = db_session.scalars(statement=statement).all()
    bills: List[Bill] = []
    for res in result:
        bill = Bill(
            id=str(res.id),
            account_id=str(res.account_id),
            biller_name=res.biller_name,
            due_date=res.due_date.isoformat(),
            amount=res.amount,
        )

        bills.append(bill)
    
    return bills

def update_bill(user_id: str, bill_id:str, request: UpdateBillRequest) -> Bill: 
    user = db_session.get(Users, user_id)
    if user is None:
        raise UserNotFoundException(id=user_id)
    
    bill = db_session.get(Bills, bill_id)
    if bill is None:
        raise BillNotFoundException(bill_id=bill_id)

    if request.biller_name is not None:
        bill.biller_name = request.biller_name
    if request.amount is not None:
        bill.amount = request.amount
    if request.due_date is not None:
        bill.due_date = request.due_date

    db_session.commit()
    updated = Bill(
        id=str(bill.id),
        account_id=str(bill.account_id),
        biller_name=bill.biller_name,
        due_date=bill.due_date.isoformat(),
        amount=bill.amount,
    )

    return updated

def get_bill(user_id: str, bill_id: str) -> Bill:

    user = db_session.get(Users, user_id)
    if user is None:
        raise UserNotFoundException(id=user_id)
    
    bill = db_session.get(Bills, bill_id)
    if bill is None:
        raise BillNotFoundException(bill_id=bill_id)

    return Bill(
        id=str(bill.id),
        account_id=str(bill.account_id),
        biller_name=bill.biller_name,
        due_date=bill.due_date.isoformat(),
        amount=bill.amount,
    )

def delete_bill(user_id: str, bill_id: str) -> bool:
    user = db_session.get(Users, user_id)
    if user is None:
        raise UserNotFoundException(id=user_id)
    
    bill = db_session.get(Bills, bill_id)
    if bill is None:
        raise BillNotFoundException(bill_id=bill_id)
    
    db_session.delete(bill)
    db_session.commit()
    return True