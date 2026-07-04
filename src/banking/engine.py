"""BankingEngine: the public API of the domain layer."""

from banking.accounts import AccountRegistry, Payment
from banking.cashbacks import (
    CASHBACK_DELAY_MS,
    CashbackQueue,
    PendingCashback,
    cashback_amount,
)


def format_top_spenders(entries: list[tuple[str, int]]) -> list[str]:
    """Render top_spenders results in the spec's exact string format."""
    return [f"{account_id}({total})" for account_id, total in entries]


class BankingEngine:
    def __init__(self) -> None:
        self._registry = AccountRegistry()
        self._cashbacks = CashbackQueue()
        self._payments: dict[str, Payment] = {}
        self._payment_counter = 0

    # ── Settlement ───────────────────────────────────────────

    def _settle(self, current_timestamp: int) -> None:
        """Apply every cashback due at or before current_timestamp.
        Called at the top of EVERY public operation."""
        for cb in self._cashbacks.pop_due(current_timestamp):
            account = self._registry.resolve(cb.account_id)
            account.balance += cb.amount
            account.snapshot(cb.execute_at)
            self._payments[cb.payment_id].cashback_applied = True

    # ── Level 1 ──────────────────────────────────────────────

    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._settle(timestamp)
        return self._registry.create(timestamp, account_id)

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._settle(timestamp)
        account = self._registry.get(account_id)
        if account is None or not account.is_active:
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
        self._settle(timestamp)
        if source_account_id == target_account_id:
            return None
        source = self._registry.get(source_account_id)
        target = self._registry.get(target_account_id)
        if source is None or target is None or not source.is_active or not target.is_active:
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
        self._settle(timestamp)
        accounts = self._registry.active_accounts()
        ranked = sorted(
            accounts,
            key=lambda acc: (-acc.total_outgoing, acc.account_id),
        )
        return [(acc.account_id, acc.total_outgoing) for acc in ranked[:n]]

    # ── Level 3 ──────────────────────────────────────────────

    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        self._settle(timestamp)
        account = self._registry.get(account_id)
        if account is None or not account.is_active or account.balance < amount:
            return None

        account.balance -= amount
        account.total_outgoing += amount
        account.snapshot(timestamp)

        self._payment_counter += 1
        payment_id = f"payment{self._payment_counter}"
        cashback_at = timestamp + CASHBACK_DELAY_MS

        self._payments[payment_id] = Payment(
            payment_id=payment_id,
            account_id=account_id,
            amount=amount,
            cashback_at=cashback_at,
        )
        self._cashbacks.schedule(
            PendingCashback(
                execute_at=cashback_at,
                account_id=account_id,
                amount=cashback_amount(amount),
                payment_id=payment_id,
            )
        )
        return payment_id

    def get_payment_status(
        self, timestamp: int, account_id: str, payment_id: str
    ) -> str | None:
        self._settle(timestamp)
        holder = self._registry.get(account_id)
        if holder is None or not holder.is_active:
            return None
        payment = self._payments.get(payment_id)
        if payment is None:
            return None
        owner = self._registry.resolve(payment.account_id)
        if owner is None or owner.account_id != account_id:
            return None
        return "CASHBACK_RECEIVED" if payment.cashback_applied else "IN_PROGRESS"
    

    # ── Level 4 ──────────────────────────────────────────────

    def merge_accounts(
        self, timestamp: int, account_id1: str, account_id2: str
    ) -> bool:
        self._settle(timestamp)
        if account_id1 == account_id2:
            return False
        primary = self._registry.get(account_id1)
        absorbed = self._registry.get(account_id2)
        if primary is None or absorbed is None:
            return False
        if not primary.is_active or not absorbed.is_active:
            return False

        primary.balance += absorbed.balance
        primary.total_outgoing += absorbed.total_outgoing
        absorbed.balance = 0

        primary.snapshot(timestamp)
        absorbed.snapshot(timestamp)

        absorbed.merged_into = account_id1
        absorbed.merged_at = timestamp
        return True

    def get_balance(
        self, timestamp: int, account_id: str, time_at: int
    ) -> int | None:
        self._settle(timestamp)
        account = self._registry.get(account_id)
        if account is None:
            return None
        return account.history.balance_at(time_at)