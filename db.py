
categories_and_aliases = {
    'продукты': ['еда', 'продукты', 'products'],
    'кафе': ['кафе', 'рест ', 'ресторан', 'мак', 'макдональдс', 'kfc'],
    'общ. транспорт': ['автобус', 'метро', 'transport', 'общ. транспорт'],
    'телефон': ['телефон', 'связь', 'phone'],
    'интернет': ['инет', 'inet', 'интернет', 'internet'],
    'подписки': ['подписки', 'spotify', 'споти', 'подписки'],
    'обед': ['обед', 'столовая', 'dinner'],
    'такси': ['такси', 'такса', 'тэха', 'taxi'],
    'прочее': ['прочее', 'other']
}

expenses = {}


def insert_expense(ex_id: int, cash: int, category_name: str, time: str):
    expenses[ex_id] = [cash, category_name, time]
