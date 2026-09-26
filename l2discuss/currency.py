from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext

CURRENCIES = ("RUB", "USD", "EUR")
CENT = Decimal("0.01")
MAX_AMOUNT = Decimal("1000000000000")
MIN_RATE = Decimal("0.0001")
MAX_RATE = Decimal("1000000")


def number(value):
    try:
        result = Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError):
        raise ValueError("Введите корректное число.") from None
    if not result.is_finite():
        raise ValueError("Число должно быть конечным.")
    return result


def convert(amount, source, usd_rate, eur_rate):
    """Курсы в рублях за единицу валюты; результат округляется до копеек."""
    if source not in CURRENCIES:
        raise ValueError("Неизвестная валюта.")
    amount = number(amount)
    usd_rate, eur_rate = number(usd_rate), number(eur_rate)
    if not 0 <= amount <= MAX_AMOUNT:
        raise ValueError("Сумма должна быть от 0 до 1 000 000 000 000.")
    if not all(MIN_RATE <= rate <= MAX_RATE for rate in (usd_rate, eur_rate)):
        raise ValueError("Курс должен быть от 0,0001 до 1 000 000 рублей.")
    rates = {"RUB": Decimal(1), "USD": usd_rate, "EUR": eur_rate}
    with localcontext() as context:
        context.prec = 40
        rubles = amount * rates[source]
        values = {
            code: (rubles / rate).quantize(CENT, rounding=ROUND_HALF_UP)
            for code, rate in rates.items()
        }
    if any(value > MAX_AMOUNT for value in values.values()):
        raise ValueError("Результат превышает лимит суммы. Уменьшите сумму или измените курс.")
    return values
