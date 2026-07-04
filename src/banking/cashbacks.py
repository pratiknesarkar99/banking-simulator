"""Pending cashback scheduling via min-heap, keyed on execution time."""

import heapq
from dataclasses import dataclass, field

CASHBACK_DELAY_MS = 24 * 60 * 60 * 1000  # 86_400_000


def cashback_amount(payment_amount: int) -> int:
    """2% of the payment, rounded down. Integer math avoids float
    representation issues entirely."""
    return payment_amount * 2 // 100


@dataclass(order=True)
class PendingCashback:
    execute_at: int
    account_id: str = field(compare=False)
    amount: int = field(compare=False)
    payment_id: str = field(compare=False)


class CashbackQueue:
    """Min-heap of pending cashbacks ordered by execute_at."""

    def __init__(self) -> None:
        self._heap: list[PendingCashback] = []

    def schedule(self, cashback: PendingCashback) -> None:
        heapq.heappush(self._heap, cashback)

    def pop_due(self, current_timestamp: int) -> list[PendingCashback]:
        """Remove and return all cashbacks due at or before
        current_timestamp, in scheduled order.
        """
        due: list[PendingCashback] = []
        while self._heap and self._heap[0].execute_at <= current_timestamp:
            due.append(heapq.heappop(self._heap))
        return due