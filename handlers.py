from aiogram import types
from aiogram.utils.markdown import text, italic
from aiogram.utils.emoji import emojize

from dispatcher import dp, bot
import exceptions
import expenses
import diagram
import keyboards as kb
from categories import Categories
from botDb import BotDB


@dp.message_handler(commands=['start'])
async def show_today_expenses(message: types.Message):
    """Выводит внесенные расходы за день"""
    if not BotDB().user_exists(message.from_user.id):
        BotDB().add_user(message.from_user.id)
    await send_welcome(message)


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    """This handler will be called when user sends `/start` or `/help` command"""
    await message.answer(text(
        emojize(f"Бот для учёта финансов :star:\n\n"),
        italic("Добавить расход: 999 продукты\n"
               "Сегодняшняя статистика: /today\n"
               "За текущий месяц: /month\n"
               "Последние внесённые расходы: /last\n"
               "Диаграмма расходов: /diagram\n"
               "Установить расход в день: /daily cash\n"
               "Категории трат: /categories")), parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['today'])
async def show_today_expenses(message: types.Message):
    """Выводит внесенные расходы за день"""
    answer_message = expenses.get_day_statistics(message.from_user.id)
    await message.answer(answer_message)


@dp.message_handler(commands=['month'])
async def show_month_expenses(message: types.Message):
    """Выводит внесенные расходы за месяц"""
    month_statistics = expenses.get_month_statistics(message.from_user.id)
    if not month_statistics:
        answer_message = "В этом месяце нет расходов"
        await message.answer(answer_message)
        return
    answer_message = f"Расходы за месяц\nВсего: {month_statistics}"
    await message.answer(answer_message, reply_markup=kb.inline_kb_month)


@dp.message_handler(commands=['last'])
async def list_expenses(message: types.Message):
    """Отправляет последние несколько записей о расходах"""
    last_expenses = expenses.last(message.from_user.id)
    if not last_expenses:
        await message.answer("Расходы ещё не заведены")
        return
    last_expenses_rows = [
        f"{expense.cash} руб. на {expense.category} — нажми "
        f"/del{expense.ex_id} для удаления"
        for expense in last_expenses]
    answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* " \
        .join(last_expenses_rows)
    await message.answer(answer_message)


@dp.message_handler(commands=['daily'])
async def daily_expense(message: types.Message):
    """Устанавливает базовый расход в день и выводит сообщение"""
    try:
        answer_message = expenses.set_daily_limit(message.text, message.from_user.id)
    except exceptions.UncorrectMessage as e:
        await message.reply(f'{str(e)}, напиши типо: /daily 500')
        return
    await message.answer(answer_message, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['diagram'])
async def show_diagram(message: types.Message):
    """Рисует диаграмму расходов"""
    diagram_name = diagram.save_diagram(message.from_user.id)
    if diagram_name:
        reply_markup = kb.get_diagram_keyboard(message.chat.id)
        await message.answer("Diagram", reply_markup=reply_markup)
    else:
        await message.answer("Расходы еще не заведены")


@dp.message_handler(commands=['categories'])
async def show_categories(message: types.Message):
    """Выводит категории трат"""
    categories = Categories().get_all_categories()
    answer_message = "Категории трат:\n\n-- " + \
        ("\n-- ".join([emojize(c.emoji) + ' ' + c.name
                       for c in categories]))
    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    """Удаляет одну запись о расходе по её идентификатору"""
    try:
        row_id = int(message.text[4:])
    except ValueError:
        await message.reply(emojize('Не понял :face_with_raised_eyebrow:'))
        return
    expenses.delete_expense(row_id, message.from_user.id)
    answer_message = "Удалил"
    await message.answer(answer_message)


@dp.message_handler()
async def add_expense(message: types.Message):
    """Добавляет расход"""
    try:
        expense = expenses.add_expense(message.text, message.from_user.id)
    except exceptions.UncorrectMessage as e:
        await message.reply(str(e)+', напиши типо: 100 такси')
        return
    answer_message = emojize(f"Добавил траты: {expense.cash}₽ на {expense.category}:white_check_mark:\n") +\
        expenses.calculate_avalible_expenses(message.from_user.id)
    await message.answer(answer_message, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(content_types=types.message.ContentType.ANY)
async def unknown_message(msg: types.Message):
    """Отвечает на разные типы сообщений"""
    message_text = emojize(f'Я не знаю, что с этим делать :face_with_symbols_on_mouth:,\n'
                           f'Я просто напомню что есть /help')
    await msg.reply(message_text)


@dp.callback_query_handler(text="month_expenses")
async def send_month_expenses(call: types.CallbackQuery):
    """Выводит суммы расходов по дням"""
    await call.message.answer(kb.month_btn_data(call.from_user.id))
    await call.answer()


@dp.callback_query_handler(kb.callback_data_diagram.filter(filter='diagram_month'))
async def send_diagram_month(call: types.CallbackQuery, callback_data: dict):
    """Отправляет диаграмму о расходах за месяц"""
    chat_id = callback_data['chat_id']
    diagram_name = diagram.save_diagram(call.from_user.id, 'month')
    await bot.send_photo(chat_id=chat_id, photo=open(diagram_name, 'rb'),
                         caption='Диаграмма за месяц')
    await call.answer()
    diagram.delete_diagram()


@dp.callback_query_handler(kb.callback_data_diagram.filter(filter='diagram_year'))
async def send_diagram_year(call: types.CallbackQuery, callback_data: dict):
    """Отправляет диаграмму о расходах за год"""
    chat_id = callback_data['chat_id']
    diagram_name = diagram.save_diagram(call.from_user.id, 'year')
    await bot.send_photo(chat_id=chat_id, photo=open(diagram_name, 'rb'),
                         caption='Диаграмма за год')
    await call.answer()
    diagram.delete_diagram()
