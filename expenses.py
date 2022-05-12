import re
from functools import reduce
from typing import NamedTuple, List, Optional, Match
from aiogram.utils.emoji import emojize

from botDb import BotDB
from exceptions import UncorrectMessage
from categories import Categories
import datetime_functions as gf


class Message(NamedTuple):
    """Структура сообщения"""
    cash: int
    category: str


class Expense(NamedTuple):
    """Структура расхода"""
    ex_id: Optional[int]
    cash: int
    category: str


def add_expense(raw_message: str, user_id) -> Expense:
    """Добавляет расход в бд"""
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(parsed_message.category)
    inserted_row_id = BotDB().insert("expense", {
        "user_id": BotDB().get_user_id(user_id),
        "cash": parsed_message.cash,
        "category": category.name,
        "created": gf.get_formated_now(),
        "raw_text": raw_message
    })
    return Expense(ex_id=None, cash=parsed_message.cash, category=category.name)


def get_month_statistics(user_id) -> int:
    """Возвращает статистику за месяц"""
    all_cash = _get_month_expenses_cash(user_id)
    return all_cash


def get_day_statistics(user_id) -> str:
    """Возвращает статистику за день"""
    day_expenses = _get_day_expenses(user_id)
    if not day_expenses:
        return "Сегодня расходов нет"
    all_cash = 0
    for expense in day_expenses:
        all_cash += expense.cash

    return (f"Расходы сегодня:\n\n" +
            ("\n".join([str(e.cash) + '₽' + ' ' + e.category for e in day_expenses])) +
            f"\nВсего - {all_cash}₽")


def last(user_id) -> List[Expense]:
    """Возвращает последние несколько расходов"""
    rows = BotDB().fetchall("expense e left join category c on c.name=e.category ",
                          "e.id e.cash c.name".split(),
                          user_id,
                          "order by id desc limit 5")
    last_expenses = [Expense(ex_id=row.get('e.id'), cash=row.get('e.cash'),
                             category=row.get('c.name')) for row in rows]
    return last_expenses


def delete_expense(row_id: int, user_id) -> None:
    """Удаляет расход по его идентификатору"""
    BotDB().delete("expense", row_id, user_id)


def set_daily_limit(message: str, user_id) -> str:
    """Устанавливается базовый расход в день"""
    parsed_message = _parse_message(message, 1)
    BotDB().update_daily_limit(user_id, parsed_message.cash)
    answer_message = f"Усановил, дневной расход -- {parsed_message.cash}₽. "
    if int(parsed_message.cash) >= 500:
        return answer_message + emojize(f'Немало :new_moon_with_face:')
    elif int(parsed_message.cash) <= 100:
        return answer_message + emojize(f'Удачи :ramen:')
    return answer_message


def calculate_avalible_expenses(user_id) -> str:
    """Расчитывает сумму, которую можно сегодня потратить и не превысить дневной лимит"""
    row = BotDB().fetchall("budget", ["daily_limit"], user_id)
    if not row:
        return ''
    daily_limit = row[0].get('daily_limit')
    day_expenses = _get_day_expenses(user_id)
    spent_cash = reduce(lambda x, y: x + y, [expence.cash for expence in day_expenses])
    avalible_cash = int(daily_limit - spent_cash)
    return _avalible_expenses_message(avalible_cash)


def _avalible_expenses_message(avalible_cash: int) -> str:
    """Формирует сообщение о состоянии дневного лимита"""
    if avalible_cash < 0:
        return 'Дневной расход превышен'
    elif avalible_cash == 0:
        return 'Вы достигли дневного расхода'
    return f'Вам доступно еще {avalible_cash}₽'


def _get_day_expenses(user_id) -> List[Expense]:
    """Возвращает расходы за день"""
    rows = BotDB().fetchall("expense", "id cash category".split(), user_id,
                            f"AND expense.created = '{gf.get_formated_now()}'")
    day_expenses = [Expense(ex_id=row.get('id'), cash=row.get('cash'),
                            category=row.get('category')) for row in rows]
    return day_expenses


def _get_month_expenses_cash(user_id) -> int:
    """Возвращает сумму расходов за месяц"""
    result = 0
    rows = BotDB().fetchall("expense", ["cash"],
                          user_id,
                          f"AND expense.created like '%{gf.get_month_and_year()}'")
    if not rows:
        return result
    result = reduce(lambda x, y: x + y, [row.get('cash') for row in rows])
    return result


def _parse_message(raw_message: str, type_message=0) -> Message:
    """Парсит сообщение"""
    regex_result = _regular_result(raw_message, type_message)
    if not regex_result or not regex_result.group(0) or not regex_result.group(1) \
            or not regex_result.group(2):
        my_answer = emojize('Не понял :face_with_raised_eyebrow:')
        raise UncorrectMessage(my_answer)
    if type_message:
        cash = regex_result.group(2)
        category = regex_result.group(1)
        return Message(cash=cash, category=category)
    cash = int(regex_result.group(1))
    category = regex_result.group(2).strip().lower()
    return Message(cash=cash, category=category)


def _regular_result(raw_message: str, type_message) -> Match[str]:
    """Возвращает результат регулярного выражения"""
    regex_result = re.match(r"([\d ]+) (.*)", raw_message)
    if type_message:
        regex_result = re.search(r"(/daily) (\d+$)", raw_message)
    return regex_result
