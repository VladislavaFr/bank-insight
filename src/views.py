import logging
from typing import Optional, List
from datetime import datetime
import pandas as pd
from .utils import to_json, get_currency_rates, get_stock_prices, filter_transactions_by_date

logging.basicConfig(level=logging.INFO)

# Файл Excel с транзакциями
EXCEL_FILE = "data/operations.xlsx"

# Настройки пользователя (валюты и акции)
USER_SETTINGS_FILE = "user_settings.json"


def load_user_settings() -> dict:
    """Загрузка пользовательских настроек для валют и акций."""
    try:
        with open(USER_SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Ошибка загрузки user_settings.json: {e}")
        return {"user_currencies": [], "user_stocks": []}


def load_transactions() -> pd.DataFrame:
    """Загрузка транзакций из Excel."""
    try:
        df = pd.read_excel(EXCEL_FILE)
        return df
    except Exception as e:
        logging.error(f"Ошибка загрузки Excel: {e}")
        return pd.DataFrame()


def greeting_by_time(hour: int) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def main_page(date_str: str) -> dict:
    """
    Главная страница: приветствие, карты, топ-5 транзакций, валюты и акции.
    :param date_str: строка даты в формате YYYY-MM-DD HH:MM:SS
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logging.error("Неверный формат даты")
        return {}

    df = load_transactions()

    # Фильтруем транзакции с начала месяца до указанной даты
    start_date = dt.replace(day=1).strftime("%Y-%m-%d")
    end_date = dt.strftime("%Y-%m-%d")
    df_filtered = filter_transactions_by_date(df, start_date, end_date)

    # Приветствие
    greeting = greeting_by_time(dt.hour)

    # Карты: последние 4 цифры, сумма расходов и кешбэк
    cards = []
    for card_number, group in df_filtered.groupby("Номер карты"):
        total_spent = group["Сумма операции"].sum()
        cards.append({
            "last_digits": str(card_number)[-4:],
            "total_spent": round(total_spent, 2),
            "cashback": round(total_spent / 100, 2)  # 1 рубль на 100 рублей
        })

    # Топ-5 транзакций по сумме
    top_transactions = df_filtered.sort_values(by="Сумма операции", ascending=False).head(5)
    top_list = top_transactions[["Дата операции", "Сумма операции", "Категория", "Описание"]].to_dict(orient="records")

    # Валюты и акции
    user_settings = load_user_settings()
    currency_rates = get_currency_rates(user_settings.get("user_currencies", []))
    stock_prices = get_stock_prices(user_settings.get("user_stocks", []))

    return {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_list,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }


def events_page(date_str: str, period: str = "M") -> dict:
    """
    Страница 'События': расходы, поступления, валюты и акции.
    :param date_str: строка даты в формате YYYY-MM-DD
    :param period: W/M/Y/ALL — неделя/месяц/год/все данные
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        logging.error("Неверный формат даты")
        return {}

    df = load_transactions()

    # Определяем период фильтрации
    if period == "W":  # неделя
        start_date = (dt - pd.Timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
    elif period == "M":  # месяц
        start_date = dt.replace(day=1).strftime("%Y-%m-%d")
    elif period == "Y":  # год
        start_date = dt.replace(month=1, day=1).strftime("%Y-%m-%d")
    else:  # ALL
        start_date = df["Дата операции"].min().strftime("%Y-%m-%d")
    end_date = dt.strftime("%Y-%m-%d")

    df_filtered = filter_transactions_by_date(df, start_date, end_date)

    # Расходы
    expenses_df = df_filtered[df_filtered["Сумма операции"] < 0]
    expenses_total = round(expenses_df["Сумма операции"].sum(), 0)
    top_categories = expenses_df.groupby("Категория")["Сумма операции"].sum().abs().sort_values(ascending=False)
    main_expenses = [{"category": k, "amount": round(v, 0)} for k, v in top_categories.head(7).items()]
    other_amount = round(top_categories.iloc[7:].sum(), 0) if len(top_categories) > 7 else 0
    if other_amount:
        main_expenses.append({"category": "Остальное", "amount": other_amount})

    transfers_df = expenses_df[expenses_df["Категория"].isin(["Наличные", "Переводы"])]
    transfers_and_cash = [{"category": k, "amount": round(v, 0)} for k, v in
                          transfers_df.groupby("Категория")["Сумма операции"].sum().abs().items()]

    # Поступления
    income_df = df_filtered[df_filtered["Сумма операции"] > 0]
    income_total = round(income_df["Сумма операции"].sum(), 0)
    main_income = [{"category": k, "amount": round(v, 0)} for k, v in
                   income_df.groupby("Категория")["Сумма операции"].sum().items()]

    # Валюты и акции
    user_settings = load_user_settings()
    currency_rates = get_currency_rates(user_settings.get("user_currencies", []))
    stock_prices = get_stock_prices(user_settings.get("user_stocks", []))

    return {
        "expenses": {
            "total_amount": expenses_total,
            "main": main_expenses,
            "transfers_and_cash": transfers_and_cash
        },
        "income": {
            "total_amount": income_total,
            "main": main_income
        },
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }