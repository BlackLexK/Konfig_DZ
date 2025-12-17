import sys
import re
import yaml




class ConfigSyntaxError(Exception):
    pass


# ЛЕКСИЧЕСКИЙ АНАЛИЗ (разбиение на токены)

# Описание токенов
TOKENS = [
    ("NUMBER",  r"[+-]?\d+\.\d+"),   
    ("NAME",    r"[_a-zA-Z]+"),      
    ("LPAREN",  r"\("),             
    ("RPAREN",  r"\)"),             
    ("LBRACE",  r"\@\{"),            
    ("RBRACE",  r"\}"),             
    ("COMMA",   r","),               
    ("SEMI",    r";"),              
    ("EQUAL",   r"="),              
    ("DOLLAR",  r"\$"),             
    ("OP",      r"[+\-*/]"),        
    ("SKIP",    r"[ \t\n]+"),         
]

# Общая регулярка 
TOKEN_REGEX = re.compile(
    "|".join(f"(?P<{name}>{regex})" for name, regex in TOKENS)
)


def tokenize(text):
    for match in TOKEN_REGEX.finditer(text):
        token_type = match.lastgroup
        token_value = match.group()

        if token_type == "SKIP":
            continue

        yield token_type, token_value

    yield "EOF", ""




class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.position = 0
        self.constants = {}  

    
    def current(self):
        return self.tokens[self.position]

    def consume(self, expected_type):
        token_type, token_value = self.current()

        if token_type != expected_type:
            raise ConfigSyntaxError(
                f"Ожидался {expected_type}, получено {token_type}"
            )

        self.position += 1
        return token_value


    
    def parse(self):
        result = {}

        while self.current()[0] != "EOF":
            name, value = self.parse_assignment()
            result[name] = value
            self.constants[name] = value

        return result


    # имя = значение;

    def parse_assignment(self):
        name = self.consume("NAME")
        self.consume("EQUAL")
        value = self.parse_value()
        self.consume("SEMI")
        return name, value


    # Разбор значения

    def parse_value(self):
        token_type, token_value = self.current()

        # Число
        if token_type == "NUMBER":
            self.consume("NUMBER")
            return float(token_value)

        # Использование константы
        if token_type == "NAME":
            self.consume("NAME")
            if token_value not in self.constants:
                raise ConfigSyntaxError(
                    f"Неизвестная константа: {token_value}"
                )
            return self.constants[token_value]

        # Массив
        if token_type == "LPAREN":
            return self.parse_array()

        # Словарь
        if token_type == "LBRACE":
            return self.parse_dict()

        # Константное выражение
        if token_type == "DOLLAR":
            return self.parse_expression()

        raise ConfigSyntaxError("Недопустимое значение")


    # ( значение, значение, ... )

    def parse_array(self):
        self.consume("LPAREN")
        items = []

        if self.current()[0] != "RPAREN":
            items.append(self.parse_value())

            while self.current()[0] == "COMMA":
                self.consume("COMMA")
                items.append(self.parse_value())

        self.consume("RPAREN")
        return items


    # @{ имя = значение; ... }

    def parse_dict(self):
        self.consume("LBRACE")
        result = {}

        while self.current()[0] != "RBRACE":
            key = self.consume("NAME")
            self.consume("EQUAL")
            value = self.parse_value()
            self.consume("SEMI")
            result[key] = value

        self.consume("RBRACE")
        return result

    # $ + a b $
    # $ sort arr $
  
    def parse_expression(self):
        self.consume("DOLLAR")

        token_type, token_value = self.current()

        # Арифметическая операция
        if token_type == "OP":
            op = self.consume("OP")
            left = self.parse_value()
            right = self.parse_value()
            self.consume("DOLLAR")
            return self.calculate(op, left, right)

        # Функция sort
        if token_type == "NAME" and token_value == "sort":
            self.consume("NAME")
            value = self.parse_value()

            if not isinstance(value, list):
                raise ConfigSyntaxError("sort применяется только к массиву")

            self.consume("DOLLAR")
            return sorted(value)

        raise ConfigSyntaxError("Неверное константное выражение")

    # Вычисление операций
    def calculate(self, op, a, b):
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            return a / b

        raise ConfigSyntaxError(f"Неизвестная операция {op}")



def main():
    input_text = sys.stdin.read()

    try:
        tokens = tokenize(input_text)
        parser = Parser(tokens)
        data = parser.parse()

        # Вывод YAML
        print(yaml.dump(data, allow_unicode=True))

    except ConfigSyntaxError as error:
        print(f"Синтаксическая ошибка: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
