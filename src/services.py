import logging
from typing import List, Dict
from .utils import get_currency_rates, get_stock_prices

logging.basicConfig(level=logging.INFO)


def get_currencies(user_currencies: List[str]) -> Dict[str, float]:
    """Получить актуальные курсы валют для пользователя."""
    if not user_currencies:
        logging.warning("Список валют пуст")
        return {}
    rates = get_currency_rates(user_currencies)
    return rates


def get_stocks(user_stocks: List[str]) -> Dict[str, float]:
    """Получить актуальные цены акций для пользователя."""
    if not user_stocks:
        logging.warning("Список акций пуст")
        return {}
    prices = get_stock_prices(user_stocks)
    return prices