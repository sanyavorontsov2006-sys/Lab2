import re
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import requests

ROMAN_PATTERN = re.compile(
    r"\b(?=[MDCLXVI]+\b)M{0,3}(?:CM|CD|D?C{0,3})"
    r"(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})\b"
)
ROMAN_SYMBOLS = {"I": 1, "V": 5, "X": 10, "L": 50,
                 "C": 100, "D": 500, "M": 1000}


def roman_to_int(value: str) -> int:
    if not isinstance(value, str) or not value:
        raise ValueError("Римское число не должно быть пустым.")
    value = value.upper()
    if not re.fullmatch(r"[IVXLCDM]+", value):
        raise ValueError("Допустимы только символы I, V, X, L, C, D, M.")

    total = 0
    for index, symbol in enumerate(value):
        current = ROMAN_SYMBOLS[symbol]
        next_value = ROMAN_SYMBOLS[value[index + 1]] if index + 1 < len(value) else 0
        total += -current if current < next_value else current

    if int_to_roman(total) != value:
        raise ValueError(f"Некорректная запись римского числа: {value}")
    return total


def int_to_roman(number: int) -> str:
    if not isinstance(number, int) or isinstance(number, bool) or not 1 <= number <= 3999:
        raise ValueError("Число должно быть целым в диапазоне от 1 до 3999.")
    values = (
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    )
    result = []
    remainder = number
    for value, symbol in values:
        count, remainder = divmod(remainder, value)
        result.append(symbol * count)
    return "".join(result)


def find_roman_numerals(text: str) -> list[tuple[str, int]]:
    if not isinstance(text, str):
        raise TypeError("На вход требуется передать строку.")
    found = []
    for match in ROMAN_PATTERN.finditer(text.upper()):
        candidate = match.group(0)
        try:
            number = roman_to_int(candidate)
        except ValueError:
            continue
        found.append((match.group(0), number))
    return found


def read_text_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    return path.read_text(encoding="utf-8")


def fetch_url(url: str, timeout: int = 10) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Укажите корректный URL, начинающийся с http:// или https://.")
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "Date-independent-RomanFinder/1.0"},
    )
    response.raise_for_status()
    response.encoding = response.encoding or response.apparent_encoding
    return response.text


def print_results(text: str) -> None:
    results = find_roman_numerals(text)
    if not results:
        print("Римские числа не найдены.")
        return
    print(f"Найдено совпадений: {len(results)}")
    for numeral, value in results:
        print(f"  {numeral} = {value}")


def main() -> None:
    while True:
        print("\n=== RomanFinder ===")
        print("1. Проверить римское число")
        print("2. Найти римские числа в тексте")
        print("3. Найти римские числа в текстовом файле")
        print("4. Найти римские числа на веб-странице")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "0":
            print("Работа завершена.")
            break
        if choice == "1":
            value = input("Введите римское число: ").strip()
            try:
                print(f"Корректно: {value.upper()} = {roman_to_int(value)}")
            except ValueError as error:
                print(f"Ошибка: {error}")
        elif choice == "2":
            print_results(input("Введите текст: "))
        elif choice == "3":
            file_path = input("Путь к текстовому файлу: ").strip()
            try:
                print_results(read_text_file(file_path))
            except (OSError, UnicodeError) as error:
                print(f"Не удалось прочитать файл: {error}")
        elif choice == "4":
            url = input("Введите URL страницы: ").strip()
            try:
                print_results(fetch_url(url))
            except (requests.RequestException, ValueError) as error:
                print(f"Не удалось загрузить страницу: {error}")
        else:
            print("Неизвестная команда. Выберите пункт меню от 0 до 4.")


if __name__ == "__main__":
    main()
