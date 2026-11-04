# utils/formatting.py
def format_number(num: int) -> str:
    return f"{num:,}".replace(",", " ")


def format_duration(minutes: int) -> str:
    hours = minutes // 60
    mins = minutes % 60
    parts = []
    if hours:
        parts.append(f"{hours} ч")
    if mins:
        parts.append(f"{mins} мин")
    return " ".join(parts) if parts else "0 мин"