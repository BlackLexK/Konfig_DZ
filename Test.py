import pytest

from Dz import parse_config, ConfigError



def test_number():
    text = """
    a = 1.5;
    """
    result = parse_config(text)
    assert result["a"] == 1.5


def test_array():
    text = """
    arr = (1.0, 2.0, 3.5);
    """
    result = parse_config(text)
    assert result["arr"] == [1.0, 2.0, 3.5]


def test_dict():
    text = """
    cfg = @{
        x = 1.0;
        y = 2.0;
    }
    """
    result = parse_config(text)
    assert result["cfg"] == {"x": 1.0, "y": 2.0}


def test_const_reference():
    text = """
    a = 2.0;
    b = a;
    """
    result = parse_config(text)
    assert result["b"] == 2.0


def test_unknown_const():
    text = """
    a = b;
    """
    with pytest.raises(ConfigError):
        parse_config(text)


def test_addition():
    text = """
    a = 2.0;
    b = $+ a 3.0$;
    """
    result = parse_config(text)
    assert result["b"] == 5.0


def test_subtraction():
    text = """
    a = 5.0;
    b = $- a 2.0$;
    """
    result = parse_config(text)
    assert result["b"] == 3.0


def test_multiplication():
    text = """
    a = 4.0;
    b = $* a 2.5$;
    """
    result = parse_config(text)
    assert result["b"] == 10.0


def test_division():
    text = """
    a = 10.0;
    b = $/ a 2.0$;
    """
    result = parse_config(text)
    assert result["b"] == 5.0


def test_division_by_zero():
    text = """
    a = 5.0;
    b = $/ a 0.0$;
    """
    with pytest.raises(ConfigError):
        parse_config(text)



def test_sort_array():
    text = """
    arr = (3.0, 1.0, 2.0);
    sorted = $sort arr$;
    """
    result = parse_config(text)
    assert result["sorted"] == [1.0, 2.0, 3.0]


def test_sort_not_array():
    text = """
    a = 1.0;
    b = $sort a$;
    """
    with pytest.raises(ConfigError):
        parse_config(text)



def test_nested_structures():
    text = """
    base = 2.0;
    cfg = @{
        values = (3.0, 1.0, base);
        sorted = $sort values$;
        sum = $+ base 3.0$;
    }
    """
    result = parse_config(text)

    assert result["cfg"]["values"] == [3.0, 1.0, 2.0]
    assert result["cfg"]["sorted"] == [1.0, 2.0, 3.0]
    assert result["cfg"]["sum"] == 5.0



def test_syntax_error():
    text = """
    a = (1.0, 2.0;
    """
    with pytest.raises(Exception):
        parse_config(text)


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 0:
        print("\nВсе тесты пройдены успешно")


