import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import text, italic
from emoji import emojize

import emoji_functions as ef
import exceptions
import expenses
import diagram
from categories import Categories
from config import BOT_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """This handler will be called when user sends `/start` or `/help` command"""
    await message.answer(text(
        emojize(f"Бот для учёта финансов {ef.get_emoji_by_key('star')}\n\n"),
        italic("Добавить расход: 999 продукты\n"
               "Сегодняшняя статистика: /today\n"
               "За текущий месяц: /month\n"
               "Последние внесённые расходы: /last\n"
               "Удалить последний расход: /del\n"
               "Диаграмма расходов: /diagram\n"
               "Категории трат: /categories")), parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['today'])
async def show_today_expenses(message: types.Message):
    """Выводит внесенные расходы за день"""
    answer_message = expenses.get_today_statistics()
    await message.reply(answer_message)


@dp.message_handler(commands=['month'])
async def show_month_expenses(message: types.Message):
    """Выводит внесенные расходы за месяц"""
    answer_message = expenses.get_month_statistics()
    await message.reply(answer_message)


@dp.message_handler(commands=['last'])
async def show_last_expenses(message: types.Message):
    """Выводит последние внесенные расходы"""
    last_expenses = expenses.last()
    if not last_expenses:
        await message.reply("Расходы еще не заведены", parse_mode=types.ParseMode.MARKDOWN)
        return
    answer_message = "Последние траты:\n\n" + \
                     ("\n ".join([str(e.cash) + '₽' + ' ' + e.category
                                  for e in last_expenses]))
    await message.reply(answer_message)


@dp.message_handler(commands=['del'])
async def del_expense(message: types.Message):
    """Удаляет последний расход"""
    answer_message = expenses.del_last_expense()
    await message.reply(answer_message)


@dp.message_handler(commands=['diagram'])
async def show_diagram(message: types.Message):
    """Рисует диаграмму расходов"""
    diagram_name = diagram.save_diagram()
    if diagram_name:
        await bot.send_photo(chat_id=message.chat.id, photo=open(diagram_name, 'rb'))
    else:
        await message.reply("Расходы еще не заведены")
    diagram.delete_diagram()


@dp.message_handler(commands=['categories'])
async def show_categories(message: types.Message):
    """Выводит категории трат"""
    categories = Categories().get_all_categories()
    answer_message = "Категории трат:\n\n-- " + \
        ("\n-- ".join([emojize(ef.get_emoji_by_key(c.name)) + ' ' + c.name
                       for c in categories]))
    await message.answer(answer_message)


@dp.message_handler()
async def add_expense(message: types.Message):
    """Добавляет расход"""
    try:
        expense = expenses.add_expense(message.text)
    except exceptions.UncorrectMessage as e:
        await message.answer(str(e))
        return
    answer_message = f"Добавил траты: {expense.cash}₽ на {expense.category}"
    await message.reply(answer_message)


@dp.message_handler(content_types=types.message.ContentType.ANY)
async def unknown_message(msg: types.Message):
    """Отвечает на разные типы сообщений"""
    message_text = emojize(f'Я не знаю, что с этим делать {ef.get_emoji_by_key("angry")},\n'
                           f'Я просто напомню что есть /help')
    await msg.reply(message_text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
