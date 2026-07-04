"""API layer tests. Focus: translation and validation, not business logic.
The engine suite already covers domain behavior."""

import pytest
from fastapi.testclient import TestClient

import banking.api.main as api_main
from banking.api.main import create_app
from banking.engine import BankingEngine


@pytest.fixture
def client() -> TestClient:
    api_main.engine = BankingEngine()   # fresh state per test
    return TestClient(create_app())


def test_create_account_roundtrip(client):
    resp = client.post(
        "/operations/create-account", json={"timestamp": 1, "account_id": "acc1"}
    )
    assert resp.status_code == 200
    assert resp.json() == {"result": True}


def test_duplicate_account_returns_false(client):
    client.post("/operations/create-account", json={"timestamp": 1, "account_id": "a"})
    resp = client.post(
        "/operations/create-account", json={"timestamp": 2, "account_id": "a"}
    )
    assert resp.json() == {"result": False}


def test_deposit_to_missing_account_is_null(client):
    resp = client.post(
        "/operations/deposit",
        json={"timestamp": 1, "account_id": "ghost", "amount": 100},
    )
    assert resp.status_code == 200
    assert resp.json() == {"result": None}


def test_negative_amount_rejected_by_schema(client):
    resp = client.post(
        "/operations/deposit",
        json={"timestamp": 1, "account_id": "a", "amount": -50},
    )
    assert resp.status_code == 422


def test_missing_field_rejected(client):
    resp = client.post("/operations/deposit", json={"timestamp": 1})
    assert resp.status_code == 422


def test_top_spenders_both_formats(client):
    client.post("/operations/create-account", json={"timestamp": 1, "account_id": "a"})
    client.post("/operations/create-account", json={"timestamp": 2, "account_id": "b"})
    client.post(
        "/operations/deposit", json={"timestamp": 3, "account_id": "a", "amount": 500}
    )
    client.post(
        "/operations/transfer",
        json={
            "timestamp": 4,
            "source_account_id": "a",
            "target_account_id": "b",
            "amount": 200,
        },
    )
    body = client.post(
        "/operations/top-spenders", json={"timestamp": 5, "n": 2}
    ).json()
    assert body["formatted"] == ["a(200)", "b(0)"]
    assert body["result"][0] == {"account_id": "a", "total_outgoing": 200}


def test_full_spec_sequence_over_http(client):
    ops = [
        ("create-account", {"timestamp": 1, "account_id": "account1"}, True),
        ("create-account", {"timestamp": 2, "account_id": "account2"}, True),
        ("deposit", {"timestamp": 3, "account_id": "account1", "amount": 2000}, 2000),
        ("deposit", {"timestamp": 4, "account_id": "account2", "amount": 2000}, 2000),
        ("pay", {"timestamp": 5, "account_id": "account2", "amount": 300}, "payment1"),
        (
            "transfer",
            {
                "timestamp": 6,
                "source_account_id": "account1",
                "target_account_id": "account2",
                "amount": 500,
            },
            1500,
        ),
        (
            "deposit",
            {"timestamp": 86400005, "account_id": "account2", "amount": 100},
            2306,
        ),
    ]
    for path, payload, expected in ops:
        assert client.post(f"/operations/{path}", json=payload).json()["result"] == expected