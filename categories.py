from typing import NamedTuple, List
from db import categories_and_aliases


class Category(NamedTuple):
    """Структура категории"""
    name: str
    aliases: List[str]


class Categories:
    def __init__(self):
        self._categories = self._load_categories()

    def _load_categories(self) -> List[Category]:
        """Возвращает справочник категорий расходов"""
        categories = []
        for category_name in categories_and_aliases:
            categories.append(Category(name=category_name, aliases=categories_and_aliases.get(category_name)))
        return categories

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
