"""Append-only balance history with O(log n) temporal lookup."""

from bisect import bisect_right


class BalanceHistory:
    """Records (timestamp, balance_after) pairs in strictly increasing
    timestamp order. Never mutates past entries.
    """

    def __init__(self) -> None:
        self._timestamps: list[int] = []
        self._balances: list[int] = []

    def record(self, timestamp: int, balance_after: int) -> None:
        """Append a new balance snapshot.

        Timestamps arrive in strictly increasing order per the spec,
        except that multiple mutations can share one timestamp (e.g. a
        transfer touches two accounts, and cashback settlement happens
        at the moment an operation runs). In that case the latest write
        at a given timestamp wins, matching the spec rule that getBalance
        reflects the state AFTER all activity at that millisecond.
        """
        if self._timestamps and self._timestamps[-1] == timestamp:
            self._balances[-1] = balance_after
            return
        self._timestamps.append(timestamp)
        self._balances.append(balance_after)

    def balance_at(self, time_at: int) -> int | None:
        """Return the balance as of time_at, or None if no history
        existed yet at that time.
        """
        idx = bisect_right(self._timestamps, time_at)
        if idx == 0:
            return None
        return self._balances[idx - 1]