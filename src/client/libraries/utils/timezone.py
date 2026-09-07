def _weekday_sunday_zero(year, month, day):
    offsets = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)
    adjusted_year = year - 1 if month < 3 else year
    return (
        adjusted_year
        + adjusted_year // 4
        - adjusted_year // 100
        + adjusted_year // 400
        + offsets[month - 1]
        + day
    ) % 7


def _days_in_month(year, month):
    if month == 2:
        return 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
    return (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[month - 1]


def _last_sunday(year, month):
    final_day = _days_in_month(year, month)
    return final_day - _weekday_sunday_zero(year, month, final_day)


def _is_bst(year, month, day, hour):
    march = _last_sunday(year, 3)
    october = _last_sunday(year, 10)
    current = (month, day, hour)
    return current >= (3, march, 1) and current < (10, october, 1)


def _add_hour(year, month, day, hour):
    hour += 1
    if hour < 24:
        return year, month, day, hour
    hour = 0
    day += 1
    if day <= _days_in_month(year, month):
        return year, month, day, hour
    day = 1
    month += 1
    if month <= 12:
        return year, month, day, hour
    return year + 1, 1, 1, hour


def format_uk_time(utc_value):
    try:
        value = str(utc_value).strip()
        date_value, time_value = value[:19].split("T", 1)
        year, month, day = (int(part) for part in date_value.split("-"))
        hour, minute, second = (int(part) for part in time_value.split(":"))
        bst = _is_bst(year, month, day, hour)
        if bst:
            year, month, day, hour = _add_hour(year, month, day, hour)
        return "{:02d}/{:02d}/{:04d} {:02d}:{:02d} {}".format(
            day, month, year, hour, minute, "BST" if bst else "GMT"
        )
    except Exception:
        return str(utc_value)
