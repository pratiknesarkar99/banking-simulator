"""Level 1 engine tests: accounts, deposits, transfers, history recording."""

import pytest

from banking.cashbacks import CASHBACK_DELAY_MS, cashback_amount
from banking.engine import BankingEngine, format_top_spenders


@pytest.fixture
def engine() -> BankingEngine:
    return BankingEngine()


class TestCreateAccount:
    def test_creates_new_account(self, engine):
        assert engine.create_account(1, "acc1") is True

    def test_rejects_duplicate_id(self, engine):
        engine.create_account(1, "acc1")
        assert engine.create_account(2, "acc1") is False

    def test_new_account_starts_at_zero(self, engine):
        engine.create_account(1, "acc1")
        assert engine.deposit(2, "acc1", 0) == 0


class TestDeposit:
    def test_deposit_returns_new_balance(self, engine):
        engine.create_account(1, "acc1")
        assert engine.deposit(2, "acc1", 2000) == 2000

    def test_deposits_accumulate(self, engine):
        engine.create_account(1, "acc1")
        engine.deposit(2, "acc1", 2000)
        assert engine.deposit(3, "acc1", 500) == 2500

    def test_deposit_to_missing_account_returns_none(self, engine):
        assert engine.deposit(1, "ghost", 100) is None


class TestTransfer:
    @pytest.fixture
    def funded(self, engine) -> BankingEngine:
        engine.create_account(1, "acc1")
        engine.create_account(2, "acc2")
        engine.deposit(3, "acc1", 2000)
        return engine

    def test_transfer_returns_source_balance(self, funded):
        assert funded.transfer(4, "acc1", "acc2", 500) == 1500

    def test_target_receives_funds(self, funded):
        funded.transfer(4, "acc1", "acc2", 500)
        assert funded.deposit(5, "acc2", 0) == 500

    def test_same_account_rejected(self, funded):
        assert funded.transfer(4, "acc1", "acc1", 100) is None

    def test_missing_source_rejected(self, funded):
        assert funded.transfer(4, "ghost", "acc2", 100) is None

    def test_missing_target_rejected(self, funded):
        assert funded.transfer(4, "acc1", "ghost", 100) is None

    def test_insufficient_funds_rejected(self, funded):
        assert funded.transfer(4, "acc1", "acc2", 99999) is None

    def test_failed_transfer_mutates_nothing(self, funded):
        funded.transfer(4, "acc1", "acc2", 99999)
        assert funded.deposit(5, "acc1", 0) == 2000
        assert funded.deposit(6, "acc2", 0) == 0


class TestBalanceHistory:
    """History is internal until Stage 4, so we test it directly here
    to lock in the temporal semantics early."""

    def test_history_records_each_mutation(self, engine):
        engine.create_account(1, "acc1")
        engine.deposit(5, "acc1", 100)
        engine.deposit(10, "acc1", 50)
        acc = engine._registry.get("acc1")
        assert acc.history.balance_at(1) == 0
        assert acc.history.balance_at(5) == 100
        assert acc.history.balance_at(7) == 100
        assert acc.history.balance_at(10) == 150

    def test_before_creation_returns_none(self, engine):
        engine.create_account(5, "acc1")
        acc = engine._registry.get("acc1")
        assert acc.history.balance_at(3) is None

    def test_exact_timestamp_reflects_post_operation_state(self, engine):
        engine.create_account(1, "acc1")
        engine.deposit(5, "acc1", 100)
        acc = engine._registry.get("acc1")
        assert acc.history.balance_at(5) == 100


class TestTopSpenders:
    @pytest.fixture
    def busy(self, engine) -> BankingEngine:
        for i in range(1, 4):
            engine.create_account(i, f"acc{i}")
        engine.deposit(10, "acc1", 1000)
        engine.deposit(11, "acc2", 1000)
        engine.deposit(12, "acc3", 1000)
        engine.transfer(20, "acc1", "acc2", 300)   # acc1 out: 300
        engine.transfer(21, "acc2", "acc3", 300)   # acc2 out: 300
        engine.transfer(22, "acc3", "acc1", 100)   # acc3 out: 100
        return engine

    def test_ranks_by_outgoing_descending(self, busy):
        result = busy.top_spenders(30, 3)
        assert [r[0] for r in result] == ["acc1", "acc2", "acc3"]

    def test_tie_broken_alphabetically(self, busy):
        # acc1 and acc2 both have 300 outgoing; acc1 sorts first
        result = busy.top_spenders(30, 2)
        assert result == [("acc1", 300), ("acc2", 300)]

    def test_n_larger_than_account_count_returns_all(self, busy):
        result = busy.top_spenders(30, 50)
        assert len(result) == 3

    def test_deposits_do_not_count_as_outgoing(self, engine):
        engine.create_account(1, "acc1")
        engine.deposit(2, "acc1", 5000)
        assert engine.top_spenders(3, 1) == [("acc1", 0)]

    def test_received_transfers_do_not_count_as_outgoing(self, busy):
        # acc3 received 300 but only sent 100
        result = busy.top_spenders(30, 3)
        assert ("acc3", 100) in result

    def test_failed_transfers_do_not_count(self, engine):
        engine.create_account(1, "acc1")
        engine.create_account(2, "acc2")
        engine.deposit(3, "acc1", 100)
        engine.transfer(4, "acc1", "acc2", 99999)  # fails
        assert engine.top_spenders(5, 1) == [("acc1", 0)]

    def test_zero_accounts_returns_empty(self, engine):
        assert engine.top_spenders(1, 5) == []

    def test_spec_string_format(self, busy):
        formatted = format_top_spenders(busy.top_spenders(30, 3))
        assert formatted == ["acc1(300)", "acc2(300)", "acc3(100)"]


class TestCashbackAmount:
    def test_two_percent_floor(self):
        assert cashback_amount(300) == 6
        assert cashback_amount(149) == 2   # 2.98 floors to 2
        assert cashback_amount(49) == 0    # 0.98 floors to 0
        assert cashback_amount(50) == 1


class TestPay:
    @pytest.fixture
    def funded(self, engine) -> BankingEngine:
        engine.create_account(1, "acc1")
        engine.deposit(2, "acc1", 1000)
        return engine

    def test_pay_returns_sequential_ids(self, funded):
        assert funded.pay(3, "acc1", 100) == "payment1"
        assert funded.pay(4, "acc1", 100) == "payment2"

    def test_pay_deducts_balance(self, funded):
        funded.pay(3, "acc1", 100)
        assert funded.deposit(4, "acc1", 0) == 900

    def test_pay_counts_as_outgoing(self, funded):
        funded.pay(3, "acc1", 100)
        assert funded.top_spenders(4, 1) == [("acc1", 100)]

    def test_pay_missing_account_returns_none(self, engine):
        assert engine.pay(1, "ghost", 100) is None

    def test_pay_insufficient_funds_returns_none(self, funded):
        assert funded.pay(3, "acc1", 99999) is None

    def test_failed_pay_does_not_consume_counter(self, funded):
        funded.pay(3, "acc1", 99999)          # fails
        assert funded.pay(4, "acc1", 100) == "payment1"


class TestCashbackSettlement:
    @pytest.fixture
    def paid(self, engine) -> BankingEngine:
        engine.create_account(1, "acc1")
        engine.deposit(2, "acc1", 1000)
        engine.pay(5, "acc1", 300)            # cashback 6 due at 86400005
        return engine

    def test_status_in_progress_before_window(self, paid):
        assert paid.get_payment_status(100, "acc1", "payment1") == "IN_PROGRESS"

    def test_status_received_after_window(self, paid):
        t = 5 + CASHBACK_DELAY_MS
        assert paid.get_payment_status(t, "acc1", "payment1") == "CASHBACK_RECEIVED"

    def test_cashback_applied_by_unrelated_operation(self, paid):
        t = 5 + CASHBACK_DELAY_MS
        paid.create_account(t, "bystander")   # any op settles
        assert paid.deposit(t + 1, "acc1", 0) == 706

    def test_cashback_lands_at_scheduled_time_in_history(self, paid):
        t = 5 + CASHBACK_DELAY_MS
        paid.deposit(t + 1000, "acc1", 0)     # settle late
        acc = paid._registry.get("acc1")
        assert acc.history.balance_at(t) == 706
        assert acc.history.balance_at(t - 1) == 700

    def test_status_wrong_account_returns_none(self, paid):
        paid.create_account(6, "acc2")
        assert paid.get_payment_status(7, "acc2", "payment1") is None

    def test_status_unknown_payment_returns_none(self, paid):
        assert paid.get_payment_status(7, "acc1", "payment999") is None


class TestSpecExampleSequence:
    """The exact walkthrough from the problem statement."""

    def test_full_sequence(self, engine):
        assert engine.create_account(1, "account1") is True
        assert engine.create_account(2, "account2") is True
        assert engine.deposit(3, "account1", 2000) == 2000
        assert engine.deposit(4, "account2", 2000) == 2000
        assert engine.pay(5, "account2", 300) == "payment1"
        assert engine.transfer(6, "account1", "account2", 500) == 1500
        assert (
            engine.get_payment_status(13, "account2", "payment1") == "IN_PROGRESS"
        )
        assert engine.deposit(86400005, "account2", 100) == 2306


class TestMergeAccounts:
    @pytest.fixture
    def two_funded(self, engine) -> BankingEngine:
        engine.create_account(1, "acc1")
        engine.create_account(2, "acc2")
        engine.deposit(3, "acc1", 1000)
        engine.deposit(4, "acc2", 500)
        return engine

    def test_merge_combines_balances(self, two_funded):
        assert two_funded.merge_accounts(10, "acc1", "acc2") is True
        assert two_funded.deposit(11, "acc1", 0) == 1500

    def test_merge_same_account_rejected(self, two_funded):
        assert two_funded.merge_accounts(10, "acc1", "acc1") is False

    def test_merge_missing_account_rejected(self, two_funded):
        assert two_funded.merge_accounts(10, "acc1", "ghost") is False

    def test_merged_account_rejects_operations(self, two_funded):
        two_funded.merge_accounts(10, "acc1", "acc2")
        assert two_funded.deposit(11, "acc2", 100) is None
        assert two_funded.transfer(12, "acc2", "acc1", 50) is None

    def test_merge_combines_outgoing_totals(self, two_funded):
        two_funded.transfer(5, "acc1", "acc2", 200)
        two_funded.transfer(6, "acc2", "acc1", 100)
        two_funded.merge_accounts(10, "acc1", "acc2")
        assert two_funded.top_spenders(11, 1) == [("acc1", 300)]

    def test_merged_account_excluded_from_top_spenders(self, two_funded):
        two_funded.merge_accounts(10, "acc1", "acc2")
        assert len(two_funded.top_spenders(11, 10)) == 1

    def test_pending_cashback_redirects_to_primary(self, two_funded):
        two_funded.pay(5, "acc2", 300)                  # cashback 6 at 86400005
        two_funded.merge_accounts(10, "acc1", "acc2")   # acc1 absorbs acc2 (200 left)
        t = 5 + CASHBACK_DELAY_MS
        assert two_funded.deposit(t, "acc1", 0) == 1206

    def test_payment_status_follows_merge(self, two_funded):
        two_funded.pay(5, "acc2", 300)
        two_funded.merge_accounts(10, "acc1", "acc2")
        assert two_funded.get_payment_status(11, "acc1", "payment1") == "IN_PROGRESS"
        assert two_funded.get_payment_status(12, "acc2", "payment1") is None

    def test_chained_merge_resolves(self, engine):
        for i in (1, 2, 3):
            engine.create_account(i, f"acc{i}")
        engine.deposit(4, "acc3", 100)
        engine.pay(5, "acc3", 100)                      # cashback 2
        engine.merge_accounts(10, "acc2", "acc3")
        engine.merge_accounts(11, "acc1", "acc2")
        t = 5 + CASHBACK_DELAY_MS
        assert engine.deposit(t, "acc1", 0) == 2


class TestGetBalance:
    def test_balance_at_past_timestamp(self, engine):
        engine.create_account(1, "acc1")
        engine.deposit(5, "acc1", 100)
        engine.deposit(10, "acc1", 50)
        assert engine.get_balance(20, "acc1", 7) == 100

    def test_before_creation_returns_none(self, engine):
        engine.create_account(5, "acc1")
        assert engine.get_balance(10, "acc1", 3) is None

    def test_unknown_account_returns_none(self, engine):
        assert engine.get_balance(10, "ghost", 5) is None

    def test_exact_timestamp_is_post_operation(self, engine):
        engine.create_account(1, "acc1")
        engine.deposit(5, "acc1", 100)
        assert engine.get_balance(10, "acc1", 5) == 100

    def test_getbalance_triggers_settlement(self, engine):
        engine.create_account(1, "acc1")
        engine.deposit(2, "acc1", 1000)
        engine.pay(5, "acc1", 300)
        t = 5 + CASHBACK_DELAY_MS
        assert engine.get_balance(t, "acc1", t) == 706

    def test_premerger_query_is_primary_alone(self, engine):
        """Interpretation A pinned as a test."""
        engine.create_account(1, "acc1")
        engine.create_account(2, "acc2")
        engine.deposit(3, "acc1", 1000)
        engine.deposit(4, "acc2", 500)
        engine.merge_accounts(10, "acc1", "acc2")
        assert engine.get_balance(20, "acc1", 5) == 1000   # not 1500

    def test_absorbed_history_still_queryable(self, engine):
        engine.create_account(1, "acc1")
        engine.create_account(2, "acc2")
        engine.deposit(4, "acc2", 500)
        engine.merge_accounts(10, "acc1", "acc2")
        assert engine.get_balance(20, "acc2", 5) == 500
