from typing import List, Dict
import matplotlib.pyplot as plt
from os import remove

from db import expenses
from categories import Categories
from expenses import Expense


def save_diagram():
    diagram_values = _get_diagram_values()
    categories_cash = [value for value in diagram_values.values()]
    categories_labels = [key for key in diagram_values.keys()]

    fig, ax = plt.subplots()
    ax.pie(categories_cash, labels=categories_labels, autopct='%1.1f%%', textprops={'color': 'white'})
    plt.savefig('diagram.png', facecolor='black')
    if categories_labels:
        return 'diagram.png'
    return None


def delete_diagram():
    remove('diagram.png')


def _parse_expenses() -> List[Expense]:
    result = []
    for key, values in expenses.items():
        category = Categories().get_category(values[1])
        result.append(Expense(ex_id=key, cash=values[0], category=category.name))
    return result


def _get_diagram_values() -> Dict:
    parsed_expenses = _parse_expenses()
    result = {}
    category = None
    for expense in parsed_expenses:
        if expense.category == category or not category:
            cash = result.get(expense.category, 0) + expense.cash
            result[expense.category] = cash
        else:
            result[expense.category] = expense.cash
        category = expense.category
    return result
