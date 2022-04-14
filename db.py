
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


emojis = {
    'продукты': ':green_apple:',
    'кафе': ':fork_and_knife_with_plate:',
    'общ. транспорт': ':bus:',
    'телефон': ':mobile_phone:',
    'интернет': ':globe_with_meridians:',
    'подписки': ':check_mark:',
    'обед': ':pot_of_food:',
    'такси': ':taxi:',
    'прочее': ':money_bag:',
    'eyebrow': ':face_with_raised_eyebrow:',
    'angry': ':face_with_symbols_on_mouth:',
    'star': ':star:',
    'dollar': ':dollar_banknote:'
}


expenses = {}


def insert_expense(ex_id: int, cash: int, category_name: str, time: str):
    expenses[ex_id] = [cash, category_name, time]
