import re
import datetime
from functools import reduce
from typing import NamedTuple, List
from aiogram.utils.emoji import emojize

import db
from exceptions import UncorrectMessage
from categories import Categories


class Message(NamedTuple):
    cash: int
    category: str


class Expense(NamedTuple):
    ex_id: int
    cash: int
    category: str


def add_expense(raw_message: str) -> Expense:
    """Добавляет расход в дб"""
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(parsed_message.category)
    if db.expenses:
        ex_id = sorted(db.expenses.keys())[-1] + 1
    else:
        ex_id = 1
    time = _get_formated_now()
    db.insert_expense(ex_id, parsed_message.cash, category.name, time)
    return Expense(ex_id=ex_id, cash=parsed_message.cash, category=category.name)


def get_month_statistics() -> int:
    """Возвращает статистику за месяц"""
    month_expenses = find_expenses_by_time('month')
    all_cash = 0
    for expense in month_expenses:
        all_cash += expense.cash
    return all_cash


def get_today_statistics() -> str:
    """Возвращает статистику за день"""
    today_expenses = find_expenses_by_time('day')
    if not today_expenses:
        return "Сегодня расходов нет"
    all_cash = 0
    for expense in today_expenses:
        all_cash += expense.cash

    return (f"Расходы сегодня:\n\n" +
            ("\n".join([str(e.cash) + '₽' + ' ' + e.category for e in today_expenses])) +
            f"\nВсего - {all_cash}₽")


def last() -> List[Expense]:
    """Возвращает последние расходы"""
    last_expenses = [Expense(ex_id=key, cash=values[0], category=values[1])
                     for key, values in db.expenses.items() if key <= 3]
    return last_expenses


def del_last_expense() -> str:
    """Удаляет последний расход"""
    if db.expenses:
        last_expense = sorted(db.expenses.keys())[-1]
        values = db.expenses.get(last_expense)
        db.expenses.pop(last_expense)
        return f"Удалил - {values[0]}₽ {values[1]}"
    return "Расходы еще не заведены"


def set_daily_expense(message: str) -> str:
    """Устанавливается базовый расход в день"""
    parse_message = _parse_message(message, 1)
    db.daily_expense = int(parse_message.cash)
    answer_message = f"Усановил, дневной расход -- {db.daily_expense}₽. "
    if db.daily_expense >= 500:
        return answer_message + emojize(f'Немало :new_moon_with_face:')
    elif db.daily_expense <= 100:
        return answer_message + emojize(f'Удачи :ramen:')
    return answer_message


def calculate_avalible_expenses():
    """Расчет разрешенных трат"""
    if not db.daily_expense:
        return ''
    day_expenses = find_expenses_by_time('day')
    spent_cash = reduce(lambda x, y: x + y, [expence.cash for expence in day_expenses])
    avalible_cash = int(db.daily_expense - spent_cash)
    return _avalible_expenses_message(avalible_cash)


def _avalible_expenses_message(avalible_cash: int) -> str:
    if avalible_cash < 0:
        return 'Дневной расход превышен'
    elif avalible_cash == 0:
        return 'Вы достигли дневного расхода'
    return f'Вам доступно еще {avalible_cash}₽'


def find_expenses_by_time(date: str) -> List[Expense]:
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


def _parse_message(raw_message: str, type_message=0) -> Message:
    regex_result = _regular_result(raw_message, type_message)
    if not regex_result or not regex_result.group(0) or not regex_result.group(1) \
            or not regex_result.group(2):
        my_answer = emojize(f'Не понял :face_with_raised_eyebrow:')
        raise UncorrectMessage(my_answer)
    if type_message:
        cash = regex_result.group(2)
        category = regex_result.group(1)
        return Message(cash=cash, category=category)
    cash = int(regex_result.group(1))
    category = regex_result.group(2).strip().lower()
    return Message(cash=cash, category=category)


def _regular_result(raw_message: str, type_message):
    regex_result = re.match(r"([\d ]+) (.*)", raw_message)
    if type_message:
        regex_result = re.search(r"(/daily) (\d+$)", raw_message)
    return regex_result
