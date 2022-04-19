from typing import Dict
import matplotlib.pyplot as plt
from os import remove
from datetime import datetime

import db


def save_diagram(date='year'):
    diagram_values = _get_diagram_values()
    if date == 'month':
        diagram_values = _get_diagram_values(date)
    categories_cash = [value for value in diagram_values.values()]
    categories_labels = [key for key in diagram_values.keys()]

    fig, ax = plt.subplots()
    ax.pie(categories_cash, autopct='%1.1f%%')
    ax.legend(categories_labels, bbox_to_anchor=(0.92, 0.7), facecolor='w', framealpha=0.8,
              edgecolor='b', fontsize=12, title='Category', title_fontsize=15)
    plt.savefig('diagram.png', facecolor='black')
    if categories_labels:
        return 'diagram.png'
    return None


def delete_diagram():
    remove('diagram.png')


def _get_diagram_values(date='year') -> Dict:
    if date == 'month':
        rows = db.fetchall("expense", "cash category".split(),
                           f"where expense.created like '%{_get_year_and_month()}'")
    else:
        rows = db.fetchall("expense", "cash category".split(),
                           f"where expense.created like '%{_get_year()}'")
    result = {}
    for row in rows:
        category = row.get('category', 0)
        if category in result:
            result[category] += row['cash']
            continue
        result[category] = row['cash']
    return result


def _get_year() -> str:
    time = datetime.now()
    return time.strftime("%Y")[2:]


def _get_year_and_month() -> str:
    time = datetime.now()
    return time.strftime("%m-%Y")
