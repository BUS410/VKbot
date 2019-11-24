"""
    Модуль для шифрования текста с помощью рандома.
    Module for encrypting text using random.
"""

from random import choice, seed

# Constant with encryptable characters
CHARS = "№`;:1234567890!@#$%^&*()/*-+.`[]}{<>," \
        "=?'\"qwertyuiopasdfghjklzxcvbnm_" \
        "йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮQWERTYUIOPASDFGHJKLZXCVBNM\n\t "


def character_distribution(key):
    """
        Возвращает словарь, в котором левые символы перед шифрованием и правые после шифрования.
        Returns a dictionary in which left characters are before encryption and right characters are after encryption.
    """
    seed(key)  # Начальная точка рандома
    dict_chars = {}
    for text_char in CHARS:
        char = choice(CHARS)
        while char in dict_chars.values():
            char = choice(CHARS)
        dict_chars[text_char] = char
    return dict_chars


def encrypt(text, key):
    dict_chars = character_distribution(key)
    result_text = ''

    try:
        for char in text:
            result_text += dict_chars[char]
    except KeyError:
        return 'Недоустимый символ/Invalid character'

    return result_text


def decrypt(text, key):
    dict_chars = character_distribution(key)
    result_text = ''

    try:
        for char in text:
            for key, item in dict_chars.items():
                if item == char:
                    result_text += key
    except KeyError:
        return 'Недоустимый символ/Invalid character'

    return result_text
