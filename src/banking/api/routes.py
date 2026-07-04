"""Thin translation layer: JSON in, engine call, JSON out."""

from typing import Annotated

from fastapi import APIRouter, Depends

from banking.api import schemas
from banking.engine import BankingEngine, format_top_spenders

router = APIRouter()


def engine_dep() -> BankingEngine:
    from banking.api.main import get_engine
    return get_engine()


Engine = Annotated[BankingEngine, Depends(engine_dep)]


@router.post("/create-account", response_model=schemas.BoolResult)
def create_account(req: schemas.CreateAccountRequest, eng: Engine):
    return {"result": eng.create_account(req.timestamp, req.account_id)}


@router.post("/deposit", response_model=schemas.IntResult)
def deposit(req: schemas.DepositRequest, eng: Engine):
    return {"result": eng.deposit(req.timestamp, req.account_id, req.amount)}


@router.post("/transfer", response_model=schemas.IntResult)
def transfer(req: schemas.TransferRequest, eng: Engine):
    return {
        "result": eng.transfer(
            req.timestamp, req.source_account_id, req.target_account_id, req.amount
        )
    }


@router.post("/pay", response_model=schemas.StrResult)
def pay(req: schemas.PayRequest, eng: Engine):
    return {"result": eng.pay(req.timestamp, req.account_id, req.amount)}


@router.post("/payment-status", response_model=schemas.StrResult)
def payment_status(req: schemas.PaymentStatusRequest, eng: Engine):
    return {
        "result": eng.get_payment_status(req.timestamp, req.account_id, req.payment_id)
    }


@router.post("/top-spenders", response_model=schemas.TopSpendersResult)
def top_spenders(req: schemas.TopSpendersRequest, eng: Engine):
    entries = eng.top_spenders(req.timestamp, req.n)
    return {
        "result": [
            {"account_id": aid, "total_outgoing": total} for aid, total in entries
        ],
        "formatted": format_top_spenders(entries),
    }


@router.post("/merge", response_model=schemas.BoolResult)
def merge(req: schemas.MergeRequest, eng: Engine):
    return {"result": eng.merge_accounts(req.timestamp, req.account_id1, req.account_id2)}


@router.post("/balance-at", response_model=schemas.IntResult)
def balance_at(req: schemas.BalanceAtRequest, eng: Engine):
    return {"result": eng.get_balance(req.timestamp, req.account_id, req.time_at)}