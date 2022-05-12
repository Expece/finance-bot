import sqlite3
import os
from typing import Dict, List


class BotDB:

    def __init__(self):
        self.conn = sqlite3.connect(os.path.join("db", "finance.db"))
        self.cursor = self.conn.cursor()
        self.check_db_exists()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE user_id = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        return self.conn.commit()

    def insert(self, table: str, column_values: Dict):
        """Добьавляет данные в бд"""
        columns = ' ,'.join(column_values.keys())
        values = [tuple(column_values.values())]
        placeholders = ", ".join("?" * len(column_values.keys()))
        self.cursor.executemany(
            f"INSERT INTO {table} "
            f"({columns}) "
            f"VALUES ({placeholders})",
            values
        )
        return self.conn.commit()

    def fetchall(self, table: str, columns: List[str], user_id='', where='') -> List[Dict]:
        """Возвращает данные из бд"""
        columns_joined = ", ".join(columns)
        if user_id:
            self.cursor.execute(f"SELECT {columns_joined} FROM {table} "
                                f"WHERE user_id = ? " + where, (self.get_user_id(user_id),))
        else:
            self.cursor.execute(f"SELECT {columns_joined} FROM {table} " + where)
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            dict_row = {}
            for index, column in enumerate(columns):
                dict_row[column] = row[index]
            result.append(dict_row)
        return result

    def delete(self, table: str, row_id: int, user_id) -> None:
        """Удаляет строку из бд"""
        row_id = int(row_id)
        self.cursor.execute(f"delete from {table} where id={row_id} AND user_id={user_id}")
        self.conn.commit()

    def get_cursor(self):
        """Возвращает курсор"""
        return self.cursor

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()

    def _init_db(self):
        """Инициализирует БД"""
        with open("createdb.sql", "r", encoding="utf-8") as f:
            sql = f.read()
        self.cursor.executescript(sql)
        self.conn.commit()

    def check_db_exists(self):
        """Проверяет, инициализирована ли БД, если нет — инициализирует"""
        self.cursor.execute("SELECT name FROM sqlite_master "
                            "WHERE type='table' AND name='expense'")
        table_exists = self.cursor.fetchall()
        if table_exists:
            return
        self._init_db()
