def amount_validate(amount: str) -> int|str:
    """Корректировка формата суммы"""
    result = ""
    for ch in amount:
        if ch.isdigit():
            result += ch

    try:
        return int(result)
    except ValueError:
        return "error"

