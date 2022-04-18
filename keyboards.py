from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from typing import Dict

from expenses import find_expenses_by_time
from db import expenses

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
    month_expenses_id = [i.ex_id for i in find_expenses_by_time('month')]
    result = {}
    for ex_id in month_expenses_id:
        time = expenses.get(ex_id)[2]
        if time in result:
            result[time] += expenses.get(ex_id)[0]
            continue
        result[time] = expenses.get(ex_id)[0]
    return result
