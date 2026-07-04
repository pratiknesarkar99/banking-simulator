"""BankingEngine: the public API of the domain layer."""

from banking.accounts import AccountRegistry


class BankingEngine:
    def __init__(self) -> None:
        self._registry = AccountRegistry()

    # ── Level 1 ──────────────────────────────────────────────

    def create_account(self, timestamp: int, account_id: str) -> bool:
        return self._registry.create(timestamp, account_id)

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        account = self._registry.get(account_id)
        if account is None:
            return None
        account.balance += amount
        account.snapshot(timestamp)
        return account.balance

    def transfer(
        self,
        timestamp: int,
        source_account_id: str,
        target_account_id: str,
        amount: int,
    ) -> int | None:
        if source_account_id == target_account_id:
            return None
        source = self._registry.get(source_account_id)
        target = self._registry.get(target_account_id)
        if source is None or target is None:
            return None
        if source.balance < amount:
            return None

        source.balance -= amount
        source.total_outgoing += amount
        target.balance += amount
        source.snapshot(timestamp)
        target.snapshot(timestamp)
        return source.balance