from datetime import date

def parse_vk_bdate(bdate: str | None) -> date | None:
    if not bdate:
        return None

    parts = bdate.split(".")

    if len(parts) != 3:
        return None

    day, month, year = parts

    try:
        return date(
            year=int(year),
            month=int(month),
            day=int(day),
        )
    except ValueError:
        return None