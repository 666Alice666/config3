import argparse
import json
import re

# Храним константы
constants = {}

# Функция для вычисления выражений
def evaluate_expression(expression):
    try:
        # Удаляем комментарии
        expression = re.sub(r'"[^"]*"', "", expression).strip()

        # Заменяем константы в выражении на их значения
        for const in constants:
            expression = expression.replace(const, str(constants[const]))

        # Обрабатываем выражение с pow(a, b)
        # Если выражение содержит pow, заменяем его на a ** b
        if 'pow' in expression:
            expression = expression.replace('pow(', '')
            expression = expression.replace(',', ' **')
        expression = re.sub(r"pow\((\d+)\s*,\s*(\d+)\)", r"\1**\2", expression)

        # Убираем лишние пробелы и символы (например, лишние запятые)
        expression = re.sub(r"\s*,\s*", " ", expression)  # Убираем пробелы перед запятыми
        expression = expression.replace(" ,", "")  # Убираем лишние запятые
        expression = expression.replace(")", "")  # Убираем лишние закрывающие скобки

        # Оценка выражения
        return eval(expression)
    except Exception as e:
        print(f"Ошибка вычисления выражения: {expression} ({e})")
        return None


# Функция для обработки файла
def parse_input_file(input_file):
    output = {}
    current_dict = output
    stack = []  # Стек для отслеживания вложенных словарей

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Игнорируем пустые строки
            if not line:
                continue

            # Обрабатываем однострочные комментарии
            if line.startswith('"'):
                continue

            # Обрабатываем установку констант (set)
            match_set = re.match(r"set\s+([A-Z]+)\s*=\s*(\d+)", line)
            if match_set:
                const_name, const_value = match_set.groups()
                constants[const_name] = int(const_value)
                current_dict[const_name] = int(const_value)
                print(f"Set constant: {const_name} = {const_value}")
                continue

            # Обрабатываем выражения (например, VALUE = ?(BASE + FACTOR))
            match_expr = re.match(r"([A-Z]+)\s*=\s?\?\(([^)]+)\)", line)
            if match_expr:
                var_name, expression = match_expr.groups()
                value = evaluate_expression(expression)
                if value is not None:
                    current_dict[var_name] = value
                continue

            # Обрабатываем начало словаря
            match_dict_open = re.match(r"([A-Z]+)\s*=\s*{", line)
            if match_dict_open:
                dict_name = match_dict_open.group(1)
                current_dict[dict_name] = {}
                stack.append(current_dict)  # Сохраняем текущий словарь
                current_dict = current_dict[dict_name]  # Переходим внутрь вложенного словаря
                continue

            # Обрабатываем конец словаря
            match_dict_end = re.match(r"}", line)
            if match_dict_end:
                if stack:
                    current_dict = stack.pop()  # Возвращаемся к предыдущему словарю
                continue

            # Добавляем остальные строки как элементы словаря
            if '=' in line:
                key, value = map(str.strip, line.split('=', 1))

                # Обрабатываем выражения и вычисляем их
                if "?" in value:
                    value = evaluate_expression(value.strip('?()'))
                current_dict[key] = value
                continue

            # Если строка не соответствует ни одному из шаблонов, выводим ошибку
            print(f"Ошибка: Некорректная структура строки: {line}")

    return output


# Функция для конвертации данных в формат JSON
def convert_to_json(data):
    return json.dumps(data, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Конвертер конфигурационного языка в JSON.")
    parser.add_argument('-i', '--input', required=True, help="Входной файл")
    parser.add_argument('-o', '--output', required=True, help="Выходной файл JSON")
    args = parser.parse_args()

    # Обрабатываем файл
    result = parse_input_file(args.input)

    # Записываем результат в файл
    with open(args.output, 'w', encoding='utf-8') as f:
        json_data = convert_to_json(result)
        f.write(json_data)

    print(f"Файл успешно создан: {args.output}")


if __name__ == "__main__":
    main()
