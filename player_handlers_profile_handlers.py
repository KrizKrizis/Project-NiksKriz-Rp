# player/handlers/profile.py
# Форматирование профиля игрока.

from db.database import db
from typing import Optional


async def format_profile(user, admin_info: Optional[dict] = None) -> str:
    lines = []

    # Имя (ник имеет приоритет)
    display_name = user.get("nickname") or f"{user['first_name']} {user['last_name']}".strip()
    lines.append(f"👤 {display_name if display_name else 'Игрок'}")

    # ID и уровень
    next_exp = user["level"] * 5
    lines.append(f"🆔 ID: {user['game_id']}")
    lines.append(f"⭐ LVL: {user['level']} (Опыт: {user['exp']}/{next_exp})")
    lines.append(f"💵 Наличные: {user['balance']} NK")

    # Банк (если выбран)
    if user["bank_name"]:
        lines.append(f"🏦 Банк ({user['bank_name']}): {user['bank_checking']} NK")

    # Жильё (если есть)
    housing = await db.fetchone(
        "SELECT h.name FROM player_housing ph JOIN housing h ON ph.housing_id = h.housing_id WHERE ph.user_id = ?",
        user["vk_id"]
    )
    if housing:
        lines.append(f"🏠 Жильё: {housing['name']}")

    # Транспорт (только активный)
    vehicle = await db.fetchone(
        "SELECT v.name FROM player_vehicles pv JOIN vehicles v ON pv.vehicle_id = v.vehicle_id WHERE pv.user_id = ? AND pv.active = 1",
        user["vk_id"]
    )
    if vehicle:
        lines.append(f"🚗 Транспорт: {vehicle['name']}")

    # Бизнесы (до 3)
    businesses = await db.fetchall(
        "SELECT name FROM businesses WHERE owner_id = ? LIMIT 3",
        user["vk_id"]
    )
    if businesses:
        lines.append(f"🏢 Бизнес: {', '.join([b['name'] for b in businesses])}")

    # Город
    lines.append(f"🏙 Город: {user['current_city']}")

    # Должность (если админ)
    if admin_info:
        lines.append(f"👑 Должность: {admin_info['position']}")

    return "\n".join(lines)