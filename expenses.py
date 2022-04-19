import re
import datetime
from functools import reduce
from typing import NamedTuple, List, Optional
from aiogram.utils.emoji import emojize

import db
from exceptions import UncorrectMessage
from categories import Categories


class Message(NamedTuple):
    cash: int
    category: str


class Expense(NamedTuple):
    ex_id: Optional[int]
    cash: int
    category: str


def add_expense(raw_message: str) -> Expense:
    """Добавляет расход в дб"""
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(parsed_message.category)
    inserted_row_id = db.insert("expense", {
        "cash": parsed_message.cash,
        "category": category.name,
        "created": _get_formated_now(),
        "raw_text": raw_message
    })
    return Expense(ex_id=None, cash=parsed_message.cash, category=category.name)


def get_month_statistics() -> int:
    """Возвращает статистику за месяц"""
    all_cash = _get_month_expenses_cash()
    return all_cash


def get_day_statistics() -> str:
    """Возвращает статистику за день"""
    day_expenses = _get_day_expenses()
    if not day_expenses:
        return "Сегодня расходов нет"
    all_cash = 0
    for expense in day_expenses:
        all_cash += expense.cash

    return (f"Расходы сегодня:\n\n" +
            ("\n".join([str(e.cash) + '₽' + ' ' + e.category for e in day_expenses])) +
            f"\nВсего - {all_cash}₽")


def last() -> List[Expense]:
    """Возвращает последние несколько расходов"""
    cursor = db.get_cursor()
    cursor.execute(
        "select e.id, e.cash, c.name "
        "from expense e left join category c "
        "on c.name=e.category "
        "order by id desc limit 5")
    rows = cursor.fetchall()
    last_expenses = [Expense(ex_id=row[0], cash=row[1], category=row[2]) for row in rows]
    return last_expenses


def delete_expense(row_id: int) -> None:
    """Удаляет сообщение по его идентификатору"""
    db.delete("expense", row_id)


def set_daily_expense(message: str) -> str:
    """Устанавливается базовый расход в день"""
    parsed_message = _parse_message(message, 1)
    cursor = db.get_cursor()
    cursor.execute(
        f"UPDATE budget SET daily_limit = {parsed_message.cash} "
        "WHERE budget.id == 1")
    answer_message = f"Усановил, дневной расход -- {parsed_message.cash}₽. "
    if int(parsed_message.cash) >= 500:
        return answer_message + emojize(f'Немало :new_moon_with_face:')
    elif int(parsed_message.cash) <= 100:
        return answer_message + emojize(f'Удачи :ramen:')
    return answer_message


def calculate_avalible_expenses():
    """Расчет разрешенных трат"""
    rows = db.fetchall("budget", ["daily_limit"])
    daily_limit = rows[0].get('daily_limit')
    if not daily_limit:
        return ''
    day_expenses = _get_day_expenses()
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


def _get_day_expenses() -> List[Expense]:
    time = _get_formated_now()
    cursor = db.get_cursor()
    cursor.execute(
        "select e.id, e.cash, e.category "
        f"from expense e where e.created == '{time}'")
    rows = cursor.fetchall()
    day_expenses = [Expense(ex_id=row[0], cash=row[1], category=row[2]) for row in rows]
    return day_expenses


def _get_month_expenses_cash() -> int:
    result = 0
    month_and_year = _get_year_and_month()
    cursor = db.get_cursor()
    cursor.execute(
        "select e.cash from expense e "
        f"where e.created like '%-{month_and_year}'")
    rows = cursor.fetchall()
    if not rows:
        return result
    result = reduce(lambda x, y: x + y, [row[0] for row in rows])
    return result


def _get_year_and_month(time='') -> str:
    if not time:
        time = _get_formated_now()
    splited_time = time.split('-')
    year_and_month = "-".join(splited_time[1:])
    return year_and_month


def _get_formated_now() -> str:
    """Возвращает сегодняшнюю дату в виде D-M-Y"""
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y")


def _parse_message(raw_message: str, type_message=0) -> Message:
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


def _regular_result(raw_message: str, type_message):
    regex_result = re.match(r"([\d ]+) (.*)", raw_message)
    if type_message:
        regex_result = re.search(r"(/daily) (\d+$)", raw_message)
    return regex_result
