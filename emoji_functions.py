from db import emojis


def get_emoji_by_key(category_name: str) -> str:
    for emoji_key in emojis.keys():
        if category_name == emoji_key:
            return emojis.get(emoji_key)
    return ''

