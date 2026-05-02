from datetime import date

def calculate_age(birth_date: date | None, today: date | None = None) -> int | None:
    if birth_date is None:
        return None

    today = today or date.today()

    age = today.year - birth_date.year

    birthday_has_not_passed = (
        today.month,
        today.day,
    ) < (
        birth_date.month,
        birth_date.day,
    )

    if birthday_has_not_passed:
        age -= 1

    return age