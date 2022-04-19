from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from typing import Dict

import db
from datetime import datetime

inline_btn_month = InlineKeyboardButton('Показать расходы по дням', callback_data='month_expenses')
inline_kb_month = InlineKeyboardMarkup().add(inline_btn_month)

callback_data_diagram = CallbackData('prefix', 'chat_id', 'filter')


def get_diagram_keyboard(chart_id):
    inline_btn_diagram_month = InlineKeyboardButton(text='Диаграмма за месяц',
            callback_data=callback_data_diagram.new(chat_id=chart_id, filter='diagram_month'))
    inline_btn_diagram_year = InlineKeyboardButton(text='Диаграмма за год',
            callback_data=callback_data_diagram.new(chat_id=chart_id, filter='diagram_year'))
    inline_kb_diagram = InlineKeyboardMarkup().add(inline_btn_diagram_month).add(inline_btn_diagram_year)
    return inline_kb_diagram


def month_btn_data() -> str:
    """Возвращает строку с дневными расходами за месяц"""
    daily_expenses = _get_daily_expenses()
    result = ''
    for day in daily_expenses:
        result += f'{day} - {daily_expenses.get(day)}\n'
    return result


def _get_daily_expenses() -> Dict:
    """Парсит expenses из дб"""
    rows = db.fetchall("expense", "cash created".split(),
                       f"where expense.created like '%{_get_year_and_month()}'")
    result = {}
    for row in rows:
        created = row.get('created')
        cash = row.get('cash')
        if result.get(created, 0):
            result[created] += cash
            continue
        result[created] = cash
    return result


def _get_year_and_month() -> str:
    time = datetime.now()
    return time.strftime("%m-%Y")
