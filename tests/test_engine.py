"""Level 1 engine tests: accounts, deposits, transfers, history recording."""

import pytest

from banking.engine import BankingEngine


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