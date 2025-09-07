import pytest
from datetime import datetime
from unittest.mock import patch
from app import views


@pytest.fixture
def sample_transactions():
    return [
        {"date": "2025-09-01", "amount": -100, "description": "Coffee"},
        {"date": "2025-09-01", "amount": 2000, "description": "Salary"},
        {"date": "2025-09-02", "amount": -300, "description": "Groceries"},
        {"date": "2025-09-03", "amount": -150, "description": "Taxi"},
        {"date": "2025-09-04", "amount": 500, "description": "Freelance"},
        {"date": "2025-09-05", "amount": -250, "description": "Restaurant"},
    ]


def test_main_page(sample_transactions):
    with patch("app.views.get_client_cards", return_value=["1234 56** **** 7890"]), \
         patch("app.views.get_transactions", return_value=sample_transactions), \
         patch("app.views.get_currency_rates", return_value={"USD": 90, "EUR": 100}), \
         patch("app.views.get_stock_prices", return_value={"AAPL": 200, "TSLA": 300}):

        result = views.main_page("2025-09-05")

        assert "greeting" in result
        assert isinstance(result["cards"], list)
        assert len(result["top_transactions"]) == 5
        assert "currency_rates" in result
        assert "stock_prices" in result


def test_events_page(sample_transactions):
    with patch("app.views.get_transactions", return_value=sample_transactions), \
         patch("app.views.get_currency_rates", return_value={"USD": 90, "EUR": 100}), \
         patch("app.views.get_stock_prices", return_value={"AAPL": 200, "TSLA": 300}), \
         patch("app.views.filter_transactions_by_date", return_value=sample_transactions):

        result = views.events_page("2025-09-05", period="M")

        assert "expenses" in result
        assert "income" in result
        assert all(isinstance(item, dict) for item in result["expenses"] + result["income"])
        assert "currency_rates" in result
        assert "stock_prices" in result