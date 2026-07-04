"""Read-only observability endpoints. These do NOT advance simulation
time and do NOT settle cashbacks. They exist for the dashboard, not
for the spec."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from banking.engine import BankingEngine

views = APIRouter()


def engine_dep() -> BankingEngine:
    from banking.api.main import get_engine
    return get_engine()


Engine = Annotated[BankingEngine, Depends(engine_dep)]


@views.get("/accounts")
def list_accounts(eng: Engine):
    return [
        {
            "account_id": acc.account_id,
            "balance": acc.balance,
            "total_outgoing": acc.total_outgoing,
            "created_at": acc.created_at,
            "merged_into": acc.merged_into,
        }
        for acc in eng._registry.all_accounts()
    ]


@views.get("/accounts/{account_id}/history")
def account_history(account_id: str, eng: Engine):
    acc = eng._registry.get(account_id)
    if acc is None:
        raise HTTPException(404)
    hist = acc.history
    return [
        {"timestamp": t, "balance": b}
        for t, b in zip(hist._timestamps, hist._balances, strict=True)
    ]


@views.get("/clock")
def clock(eng: Engine):
    return {"last_timestamp": eng.last_timestamp}