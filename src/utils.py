import json
import logging
import re
from typing import List, Dict
from datetime import datetime
import pandas as pd
import requests
from dotenv import load_dotenv
import os

# Загружаем ключи из .env
load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

logging.basicConfig(level=logging.INFO)


# -------------------- JSON --------------------
def to_json(data: dict) -> str:
    """Преобразовать словарь в JSON строку."""
    return json.dumps(data, ensure_ascii=False, indent=2)


# -------------------- Excel --------------------
def load_transactions(file_path: str) -> pd.DataFrame:
    """Загрузить транзакции из Excel."""
    df = pd.read_excel(file_path)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%Y-%m-%d")
    return df


def filter_transactions_by_date(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """Фильтровать транзакции по диапазону дат."""
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    return df[(df["Дата операции"] >= start) & (df["Дата операции"] <= end)]


# -------------------- Валюты и акции --------------------
def get_currency_rates(currencies: List[str]) -> List[Dict[str, float]]:
    """Получить текущие курсы валют через API."""
    rates = []
    for currency in currencies:
        try:
            url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={currency}&to_currency=RUB&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            rate = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
            rates.append({"currency": currency, "rate": rate})
        except Exception as e:
            logging.error(f"Ошибка при получении курса {currency}: {e}")
    return rates


def get_stock_prices(stocks: List[str]) -> List[Dict[str, float]]:
    """Получить текущие цены акций через API."""
    prices = []
    for stock in stocks:
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            price = float(data["Global Quote"]["05. price"])
            prices.append({"stock": stock, "price": price})
        except Exception as e:
            logging.error(f"Ошибка при получении цены {stock}: {e}")
    return prices


# -------------------- Поиск --------------------
def search_transactions(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """Поиск транзакций по строке."""
    mask = df["Описание"].str.contains(query, case=False, na=False) | \
           df["Категория"].str.contains(query, case=False, na=False)
    return df[mask]


def search_phone_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """Поиск транзакций с телефонными номерами."""
    phone_pattern = r"\+7\s?\d{3}\s?\d{2}-?\d{2}-?\d{2}"
    mask = df["Описание"].str.contains(phone_pattern, regex=True, na=False)
    return df[mask]


def search_transfers_to_people(df: pd.DataFrame) -> pd.DataFrame:
    """Поиск переводов физическим лицам (имя + первая буква фамилии)."""
    transfer_pattern = r"[А-ЯЁ][а-яё]+ [А-Я]\."
    mask = (df["Категория"] == "Переводы") & df["Описание"].str.contains(transfer_pattern, regex=True, na=False)
    return df[mask]
