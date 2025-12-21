from lark import Lark, Transformer, v_args
from lark.exceptions import VisitError
import yaml  # <-- добавляем для красивого вывода

GRAMMAR = r"""
start: stmt*

stmt: NAME "=" expr ";"?

?expr: NUMBER        -> number
     | NAME          -> var
     | array
     | dict
     | operation

array: "(" [expr ("," expr)*] ")"

dict: "@{" stmt* "}"

operation: "$" OP expr expr "$"
         | "$sort" expr "$"

OP: "+" | "-" | "*" | "/"

%import common.CNAME -> NAME
%import common.SIGNED_NUMBER -> NUMBER
%import common.WS
%ignore WS
"""


class ConfigError(Exception):
    pass


@v_args(inline=True)
class EvalTransformer(Transformer):
    def __init__(self):
        self.consts = {}

    def start(self, *stmts):
        return self.consts

    def stmt(self, name, value):
        name = str(name)
        self.consts[name] = value
        return name, value

    def number(self, token):
        return float(token)

    def var(self, name):
        name = str(name)
        if name not in self.consts:
            raise ConfigError(f"Неизвестная константа: {name}")
        return self.consts[name]

    def array(self, *items):
        return list(items)

    def dict(self, *stmts):
        result = {}
        for k, v in stmts:
            result[k] = v
        return result

    def operation(self, *args):
        # $sort expr$
        if len(args) == 1:
            value = args[0]
            if not isinstance(value, list):
                raise ConfigError("sort применяется только к массивам")
            return sorted(value)

        # $op a b$
        op, a, b = args
        op = str(op)

        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if b == 0:
                raise ConfigError("Деление на ноль")
            return a / b

        raise ConfigError(f"Неизвестная операция: {op}")


def parse_config(text: str):
    parser = Lark(GRAMMAR, start="start", parser="lalr")
    try:
        tree = parser.parse(text)
        return EvalTransformer().transform(tree)
    except VisitError as e:
        if isinstance(e.orig_exc, ConfigError):
            raise e.orig_exc
        raise


if __name__ == "__main__":
    import sys
    config_text = sys.stdin.read()  # читаем весь текст из stdin
    result = parse_config(config_text)
    print(yaml.dump(result, sort_keys=False))  # выводим красиво в YAML
