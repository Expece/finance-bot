from typing import Dict
import matplotlib.pyplot as plt
from os import remove

import db
import datetime_functions as gf

# Название диаграммы, оно не меняется
diagram_name = 'diagram.png'


def save_diagram(date='year') -> str or None:
    """Сохраняет диаграмму в png и возвращает ее название"""
    diagram_values = _get_diagram_values()
    if date == 'month':
        diagram_values = _get_diagram_values(date)
    categories_cash = [value for value in diagram_values.values()]
    categories_labels = [key for key in diagram_values.keys()]

    fig, ax = plt.subplots()
    ax.pie(categories_cash, autopct='%1.1f%%')
    ax.legend(categories_labels, bbox_to_anchor=(0.92, 0.7), facecolor='w', framealpha=0.8,
              edgecolor='b', fontsize=12, title='Category', title_fontsize=15)
    plt.savefig(diagram_name, facecolor='black')
    if categories_labels:
        return diagram_name
    return None


def delete_diagram():
    """Удаляет диаграмму по ее имени"""
    remove(diagram_name)


def _get_diagram_values(date='year') -> Dict:
    """Возвращает данные для диаграммы"""
    if date == 'month':
        rows = db.fetchall("expense", "cash category".split(),
                           f"where expense.created like '%{gf.get_month_and_year()}'")
    else:
        rows = db.fetchall("expense", "cash category".split(),
                           f"where expense.created like '%{gf.get_year()}'")
    result = {}
    for row in rows:
        category = row.get('category', 0)
        if category in result:
            result[category] += row['cash']
            continue
        result[category] = row['cash']
    return result
