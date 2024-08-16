# class Logger:
#     __instance = None

#     def __new__(cls, *args, **kwargs):
#         if cls.__instance is None:
#             cls.__instance = super(Logger, cls).__new__(cls)
#         return cls.__instance

#     def __init__(self, name) -> None:
#         if not hasattr(self, "name"):
#             self.name = name


# l1 = Logger("joe")
# l2 = Logger("steve")

# print(l1.name)
# print(l2.name)

# print(l1 is l2)

import os
from pathlib import Path


def cache_words(func):
    BAN_WORDS = {}

    def wrapper(filename):
        if filename not in BAN_WORDS:
            BAN_WORDS[filename] = func(filename)
        return BAN_WORDS[filename]

    return wrapper


# @cache_words
def pull_words(filename):
    """Read file and return set of words"""
    with open(filename, "r", encoding="utf8") as f:
        words = {line.strip().lower() for line in f if line.strip()}
    return words


path = os.path.join(
    f"{Path(__file__).resolve().parent}",
    "ban_words",
    "profanity_ru.txt",
)

print(pull_words(path))
