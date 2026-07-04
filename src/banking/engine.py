"""BankingEngine: the public API of the domain layer."""

from banking.accounts import AccountRegistry


def format_top_spenders(entries: list[tuple[str, int]]) -> list[str]:
    """Render top_spenders results in the spec's exact string format."""
    return [f"{account_id}({total})" for account_id, total in entries]

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
    
    # ── Level 2 ──────────────────────────────────────────────

    def top_spenders(self, timestamp: int, n: int) -> list[tuple[str, int]]:
        """Top n accounts by total outgoing, ties broken by account_id
        ascending. Returns (account_id, total_outgoing) tuples.
        """
        accounts = self._registry.all_accounts()
        ranked = sorted(
            accounts,
            key=lambda acc: (-acc.total_outgoing, acc.account_id),
        )
        return [(acc.account_id, acc.total_outgoing) for acc in ranked[:n]]