"""Request and response models. Validation happens here, not in the domain."""

from pydantic import BaseModel, Field

Timestamp = Field(ge=1, le=1_000_000_000)
Amount = Field(gt=0)


class CreateAccountRequest(BaseModel):
    timestamp: int = Timestamp
    account_id: str = Field(min_length=1)


class DepositRequest(BaseModel):
    timestamp: int = Timestamp
    account_id: str = Field(min_length=1)
    amount: int = Amount


class TransferRequest(BaseModel):
    timestamp: int = Timestamp
    source_account_id: str = Field(min_length=1)
    target_account_id: str = Field(min_length=1)
    amount: int = Amount


class PayRequest(BaseModel):
    timestamp: int = Timestamp
    account_id: str = Field(min_length=1)
    amount: int = Amount


class PaymentStatusRequest(BaseModel):
    timestamp: int = Timestamp
    account_id: str = Field(min_length=1)
    payment_id: str = Field(min_length=1)


class TopSpendersRequest(BaseModel):
    timestamp: int = Timestamp
    n: int = Field(ge=1)


class MergeRequest(BaseModel):
    timestamp: int = Timestamp
    account_id1: str = Field(min_length=1)
    account_id2: str = Field(min_length=1)


class BalanceAtRequest(BaseModel):
    timestamp: int = Timestamp
    account_id: str = Field(min_length=1)
    time_at: int = Field(ge=1)


class BoolResult(BaseModel):
    result: bool


class IntResult(BaseModel):
    result: int | None


class StrResult(BaseModel):
    result: str | None


class SpenderEntry(BaseModel):
    account_id: str
    total_outgoing: int


class TopSpendersResult(BaseModel):
    result: list[SpenderEntry]
    formatted: list[str]