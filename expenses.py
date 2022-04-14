import re
import datetime
from typing import NamedTuple, List
from emoji import emojize

import db
from exceptions import UncorrectMessage
from categories import Categories
import emoji_functions as ef


class Message(NamedTuple):
    cash: int
    category: str


class Expense(NamedTuple):
    ex_id: int
    cash: int
    category: str


def add_expense(raw_message: str) -> Expense:
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(parsed_message.category)
    if db.expenses:
        ex_id = sorted(db.expenses.keys())[-1] + 1
    else:
        ex_id = 1
    time = _get_formated_now()
    db.insert_expense(ex_id, parsed_message.cash, category.name, time)
    return Expense(ex_id=ex_id, cash=parsed_message.cash, category=category.name)


def get_month_statistics() -> str:
    month_expenses = _find_expenses_by_time('month')
    if not month_expenses:
        return "В этом месяце нет расходов"
    all_cash = 0
    for expense in month_expenses:
        all_cash += expense.cash

    return (f"Расходы за месяц:\n\n"
            f"Всего - ₽{all_cash}")


def get_today_statistics() -> str:
    today_expenses = _find_expenses_by_time('day')
    if not today_expenses:
        return "Сегодня расходов нет"
    all_cash = 0
    for expense in today_expenses:
        all_cash += expense.cash

    return (f"Расходы сегодня:\n\n"
            f"Всего - ₽{all_cash}")


def last() -> List[Expense]:
    last_expenses = [Expense(ex_id=key, cash=values[0], category=values[1])
                     for key, values in db.expenses.items() if key <= 3]
    return last_expenses


def del_last_expense() -> str:
    """Удаляет последний расход"""
    if db.expenses:
        last_expense = sorted(db.expenses.keys())[-1]
        values = db.expenses.get(last_expense)
        db.expenses.pop(last_expense)
        return f"Удалил - {values[0]} {values[1]}"
    return "Расходы еще не заведены"


def _find_expenses_by_time(date: str) -> List[Expense]:
    expenses = []
    time = _get_formated_now()
    for ex_id, values in db.expenses.items():
        if date == 'month':
            if _get_split_time(values[2]) == _get_split_time(time):
                expenses.append(Expense(ex_id=ex_id, cash=values[0], category=values[1]))
        else:
            if values[2] == time:
                expenses.append(Expense(ex_id=ex_id, cash=values[0], category=values[1]))
    return expenses


def _get_split_time(time: str) -> List[str]:
    splited_time = time.split('-')
    return splited_time[:-1]


def _get_formated_now() -> str:
    """Возвращает сегодняшнюю дату в виде D-M-Y"""
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y")


def _parse_message(raw_message: str) -> Message:
    regex_result = re.match(r"([\d ]+) (.*)", raw_message)
    if not regex_result or not regex_result.group(0) or not regex_result.group(1) \
            or not regex_result.group(2):
        my_answer = emojize(f'Не понял {ef.get_emoji_by_key("eyebrow")}')
        raise UncorrectMessage(my_answer)

    cash = int(regex_result.group(1))
    category = regex_result.group(2).strip().lower()
    return Message(cash=cash, category=category)
