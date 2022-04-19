from typing import NamedTuple, List, Dict
import db


class Category(NamedTuple):
    """Структура категории"""
    name: str
    emoji: str
    aliases: List[str]


class Categories:
    def __init__(self):
        self._categories = self._load_categories()

    def _load_categories(self) -> List[Category]:
        """Возвращает справочник категорий расходов"""
        categories = db.fetchall(
            "category", "name emoji aliases".split()
        )
        categories = self._fill_aliases(categories)
        return categories

    def _fill_aliases(self, categories: List[Dict]) -> List[Category]:
        """Заполняет по каждой категории aliases, то есть возможные
                                            названия этой категории"""
        categories_result = []
        for index, category in enumerate(categories):
            aliases = category["aliases"].split(",")
            aliases = list(filter(None, map(str.strip, aliases)))
            aliases.append(category["name"])
            categories_result.append(Category(
                name=category['name'],
                emoji=category['emoji'],
                aliases=aliases
            ))
        return categories_result

    def get_all_categories(self) -> List[Category]:
        """Возвращает справочник категорий"""
        return self._categories

    def get_category(self, category_name: str) -> Category:
        other_category = None
        for category in self._categories:
            if category.name == 'прочее':
                other_category = category
            else:
                for alias in category.aliases:
                    if category_name in alias:
                        return category
        return other_category
