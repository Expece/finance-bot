# Словарь категорий и псевдонимов
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

# Словарь эмоджи для категорий
category_emojis = {
    'продукты': ':green_apple:',
    'кафе': ':fork_and_knife_with_plate:',
    'общ. транспорт': ':bus:',
    'телефон': ':mobile_phone:',
    'интернет': ':globe_with_meridians:',
    'подписки': ':check_mark:',
    'обед': ':pot_of_food:',
    'такси': ':taxi:',
    'прочее': ':money_bag:',
}

# Запись расходов в виде: id: [cash: int,category: str, time: str]
expenses = {}

# Устанавливается базовый расход в день
daily_expense = 0


def insert_expense(ex_id: int, cash: int, category_name: str, time: str):
    """Добавить расход в expenses"""
    expenses[ex_id] = [cash, category_name, time]
