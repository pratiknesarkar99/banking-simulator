"""Account entity and registry."""

from dataclasses import dataclass, field

from banking.ledger import BalanceHistory


@dataclass
class Account:
    account_id: str
    created_at: int
    balance: int = 0
    total_outgoing: int = 0
    history: BalanceHistory = field(default_factory=BalanceHistory)
    merged_into: str | None = None
    merged_at: int | None = None

    @property
    def is_active(self) -> bool:
        return self.merged_into is None

    def snapshot(self, timestamp: int) -> None:
        self.history.record(timestamp, self.balance)

@dataclass
class Payment:
    payment_id: str
    account_id: str
    amount: int
    cashback_at: int
    cashback_applied: bool = False

class AccountRegistry:
    """Owns all accounts. The only place accounts are created or looked up."""

    def __init__(self) -> None:
        self._accounts: dict[str, Account] = {}

    def create(self, timestamp: int, account_id: str) -> bool:
        if account_id in self._accounts:
            return False
        account = Account(account_id=account_id, created_at=timestamp)
        account.snapshot(timestamp)
        self._accounts[account_id] = account
        return True

    def get(self, account_id: str) -> Account | None:
        return self._accounts.get(account_id)

    def all_accounts(self) -> list[Account]:
        return list(self._accounts.values())
    
    def resolve(self, account_id: str) -> Account | None:
        """Follow merge redirects to the current owning account.
        Returns None if the id never existed."""
        account = self._accounts.get(account_id)
        while account is not None and account.merged_into is not None:
            account = self._accounts.get(account.merged_into)
        return account

    def active_accounts(self) -> list[Account]:
        return [a for a in self._accounts.values() if a.is_active]