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

    def snapshot(self, timestamp: int) -> None:
        """Record the current balance into history at this timestamp."""
        self.history.record(timestamp, self.balance)


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