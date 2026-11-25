from calendar import monthrange
from datetime import date, timedelta
from equipment.models import EquipmentType
from django.utils.translation import gettext_lazy as translate

def calculate_valid_until(start_date: date, interval_value: int, interval_unit: str) -> date:
    if interval_value < 1:
        raise ValueError(translate('Interval must be positive.'))

    if interval_unit == EquipmentType.IntervalUnit.DAYS:
        return start_date + timedelta(days=interval_value)

    if interval_unit == EquipmentType.IntervalUnit.MONTHS:
        months = interval_value

    elif interval_unit == EquipmentType.IntervalUnit.YEARS:
        months = interval_value * 12

    else:
        raise ValueError(translate('Invalid interval unit.'))

    total_months = start_date.month - 1 + months
    year = start_date.year + total_months // 12
    month = total_months % 12 + 1
    last_day = monthrange(year, month)[1]
    day = min(start_date.day, last_day)

    return date(year, month, day)