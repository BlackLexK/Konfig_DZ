from Dz import tokenize, Parser, ConfigSyntaxError

def parse(text):
    tokens = tokenize(text)
    parser = Parser(tokens)
    return parser.parse()


def check(test_name, actual, expected):
    if actual == expected:
        print(f"[OK] {test_name}")
    else:
        print(f"[ERROR] {test_name}")
        print("  Ожидалось:", expected)
        print("  Получено :", actual)


def check_error(test_name, text):
    try:
        parse(text)
        print(f"[ERROR] {test_name} — ошибка не обнаружена")
    except ConfigSyntaxError:
        print(f"[OK] {test_name}")


# Числа
check(
    "Число",
    parse("a = 3.14;")["a"],
    3.14
)

check(
    "Отрицательное число",
    parse("a = -2.5;")["a"],
    -2.5
)

# Константы
check(
    "Использование константы",
    parse("a = 1.5; b = a;")["b"],
    1.5
)

check_error(
    "Неизвестная константа",
    "b = a;"
)

# Массивы
check(
    "Массив",
    parse("arr = (1.0, 2.0, 3.0);")["arr"],
    [1.0, 2.0, 3.0]
)

check(
    "Вложенный массив",
    parse("arr = ((1.0, 2.0), (3.0));")["arr"],
    [[1.0, 2.0], [3.0]]
)

# Словари
check(
    "Словарь",
    parse("""
        cfg = @{
            a = 1.0;
            b = 2.0;
        };
    """)["cfg"]["a"],
    1.0
)

check(
    "Вложенный словарь",
    parse("""
        cfg = @{
            inner = @{
                x = 5.0;
            };
        };
    """)["cfg"]["inner"]["x"],
    5.0
)

# Выражения
check(
    "Сложение",
    parse("a = $+ 1.0 2.0$;")["a"],
    3.0
)

check(
    "Вычитание",
    parse("a = $- 5.0 2.0$;")["a"],
    3.0
)

check(
    "Умножение",
    parse("a = $* 2.0 3.0$;")["a"],
    6.0
)

check(
    "Деление",
    parse("a = $/ 6.0 2.0$;")["a"],
    3.0
)

# Сортировка
check(
    "Сортировка массива",
    parse("arr = (3.0, 1.0, 2.0); s = $sort arr$;")["s"],
    [1.0, 2.0, 3.0]
)

check_error(
    "Ошибка sort не от массива",
    "a = $sort 1.0$;"
)


# 
check(
    "Сложная структура",
    parse("""
        base = 2.0;
        data = @{
            values = (3.0, 1.0, base);
            result = $+ base 1.0$;
            sorted = $sort (3.0, 2.0, 1.0)$;
        };
    """)["data"]["values"],
    [3.0, 1.0, 2.0]
)

# Синтаксис
check_error(
    "Нет точки с запятой",
    "a = 1.0"
)

check_error(
    "Неверное выражение",
    "a = $+ 1.0$;"
)

print("\nТестирование завершено.")
