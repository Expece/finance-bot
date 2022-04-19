import datetime


def get_formated_now() -> str:
    """Возвращает сегодняшнюю дату в виде D-M-Y"""
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y")


def get_month_and_year() -> str:
    """Возращает сегодняшнюю дату в видее M-Y"""
    now = datetime.datetime.now()
    return now.strftime("%m-%Y")


def get_year() -> str:
    """Возвращает 2 последних знаения года"""
    time = datetime.datetime.now()
    return time.strftime("%Y")[2:]
