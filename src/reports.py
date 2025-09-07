import logging
import pandas as pd
from datetime import datetime
from .utils import filter_transactions_by_date

logging.basicConfig(level=logging.INFO)


def generate_expense_report(df: pd.DataFrame, start_date: str, end_date: str) -> dict:
    """Отчёт по расходам за период."""
    df_filtered = filter_transactions_by_date(df, start_date, end_date)
    expenses_df = df_filtered[df_filtered["Сумма операции"] < 0]

    total_expenses = round(expenses_df["Сумма операции"].sum(), 0)
    top_categories = expenses_df.groupby("Категория")["Сумма операции"].sum().abs().sort_values(ascending=False)
    main_expenses = [{"category": k, "amount": round(v, 0)} for k, v in top_categories.head(7).items()]
    other_amount = round(top_categories.iloc[7:].sum(), 0) if len(top_categories) > 7 else 0
    if other_amount:
        main_expenses.append({"category": "Остальное", "amount": other_amount})

    return {
        "total_amount": total_expenses,
        "main": main_expenses
    }


def generate_income_report(df: pd.DataFrame, start_date: str, end_date: str) -> dict:
    """Отчёт по поступлениям за период."""
    df_filtered = filter_transactions_by_date(df, start_date, end_date)
    income_df = df_filtered[df_filtered["Сумма операции"] > 0]

    total_income = round(income_df["Сумма операции"].sum(), 0)
    main_income = [{"category": k, "amount": round(v, 0)} for k, v in income_df.groupby("Категория")["Сумма операции"].sum().items()]

    return {
        "total_amount": total_income,
        "main": main_income
    }