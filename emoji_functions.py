from db import emojis


def get_emoji_by_key(key: str) -> str:
    for emoji_key in emojis.keys():
        if key == emoji_key:
            return emojis.get(emoji_key)
    return ''
