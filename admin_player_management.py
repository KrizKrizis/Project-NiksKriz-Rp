# admin/player_management.py
import json
import logging
from datetime import datetime, timezone, timedelta
from vkbottle import Keyboard, Callback, KeyboardButtonColor
from db.database import db
from utils.permissions import has_permission, get_admin_info

logger = logging.getLogger(__name__)
PAGE_SIZE = 50


async def get_player_page(page: int) -> list:
    offset = (page - 1) * PAGE_SIZE
    return await db.fetchall(
        "SELECT vk_id, game_id, first_name, last_name, nickname, level, balance, bank_checking, is_blocked "
        "FROM users ORDER BY game_id LIMIT ? OFFSET ?",
        PAGE_SIZE, offset
    )


async def get_total_pages() -> int:
    total = await db.fetchone("SELECT COUNT(*) as cnt FROM users")
    count = total["cnt"] if total else 0
    return (count + PAGE_SIZE - 1) // PAGE_SIZE


async def format_player_list_page(page: int) -> tuple:
    players = await get_player_page(page)
    if not players:
        return "Игроки не найдены.", None

    lines = [f"Страница {page}"]
    for p in players:
        status = "🔴" if p["is_blocked"] else "🟢"
        nickname = p["nickname"]
        display_name = nickname if nickname else f"{p['first_name']} {p['last_name']}"
        lines.append(f"{status} {p['game_id']} | {display_name} | LVL {p['level']} | NK {p['balance']}")

    total_pages = await get_total_pages()
    keyboard = Keyboard(inline=True)
    left_color = KeyboardButtonColor.SECONDARY if page == 1 else KeyboardButtonColor.PRIMARY
    right_color = KeyboardButtonColor.SECONDARY if page >= total_pages else KeyboardButtonColor.POSITIVE

    keyboard.add(Callback("⬅️", payload={"cmd": "players_page", "page": page - 1 if page > 1 else 1}), color=left_color)
    keyboard.add(Callback("📊 Статистика", payload={"cmd": "player_stats_request"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("➡️", payload={"cmd": "players_page", "page": page + 1 if page < total_pages else page}), color=right_color)
    keyboard.row()
    keyboard.add(Callback("📋 Логи", payload={"cmd": "player_logs_request"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🔍 Поиск", payload={"cmd": "player_search_request"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("⚙️ Управление", payload={"cmd": "player_manage_request"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "founder_main"}), color=KeyboardButtonColor.SECONDARY)

    return "\n".join(lines), keyboard.get_json()


async def get_player_profile(target_id: int, viewer_id: int) -> str:
    user = await db.fetchone("SELECT * FROM users WHERE vk_id = ?", target_id)
    if not user:
        return "Игрок не найден."

    vk_link = f"https://vk.com/id{user['vk_id']}"
    vk_name = f"{user['first_name']} {user['last_name']}"
    nickname = user["nickname"] if user["nickname"] else "не указан"

    lines = [
        f"👤 ВК: {vk_name} ({vk_link})",
        f"🎭 Игровой ник: {nickname}",
        f"🆔 ID: {user['game_id']} (VK ID: {user['vk_id']})",
        f"⭐ LVL: {user['level']} (Опыт: {user['exp']}/{user['level']*5})",
        f"💵 Наличные: {user['balance']} NK",
        f"🏦 Банк: {user['bank_name'] or 'не выбран'}",
        f"🏙 Город: {user['current_city']}",
        f"📅 Регистрация: {user['registration_date']}",
    ]

    if user["current_work"]:
        lines.append(f"💼 Работа: {user['current_work']} (до {user['work_end_time']})")
    if user["is_blocked"]:
        lines.append("🔴 Заблокирован")
    if user["temporary_blocked_until"]:
        lines.append(f"⏳ Заморожен до: {user['temporary_blocked_until']}")

    if await has_permission(viewer_id, "players.view_extended"):
        lines.append(f"💳 Основной счёт: {user['bank_checking']} NK")
        lines.append(f"📈 Накопительный: {user['bank_savings']} NK")
        lines.append(f"🧾 Налоговый: {user['tax_account']} NK")
        lines.append(f"⭐ Репутация: {user['reputation']}")

        housing = await db.fetchone(
            "SELECT h.name FROM player_housing ph JOIN housing h ON ph.housing_id = h.housing_id WHERE ph.user_id = ?",
            target_id
        )
        if housing:
            lines.append(f"🏠 Жильё: {housing['name']}")

        vehicles = await db.fetchall(
            "SELECT v.name FROM player_vehicles pv JOIN vehicles v ON pv.vehicle_id = v.vehicle_id WHERE pv.user_id = ?",
            target_id
        )
        if vehicles:
            lines.append(f"🚗 Транспорт: {', '.join([v['name'] for v in vehicles])}")

        businesses = await db.fetchall("SELECT name FROM businesses WHERE owner_id = ?", target_id)
        if businesses:
            lines.append(f"🏢 Бизнесы: {', '.join([b['name'] for b in businesses])}")

        inventory = await db.fetchall(
            "SELECT i.name, inv.quantity FROM inventory inv JOIN items i ON inv.item_id = i.item_id WHERE inv.user_id = ?",
            target_id
        )
        if inventory:
            inv_list = [f"{item['name']} (x{item['quantity']})" for item in inventory]
            lines.append(f"🎒 Инвентарь: {', '.join(inv_list[:5])}{'...' if len(inv_list) > 5 else ''}")

        transactions = await db.fetchall(
            "SELECT * FROM transactions WHERE sender_id = ? OR receiver_id = ? ORDER BY id DESC LIMIT 5",
            target_id, target_id
        )
        if transactions:
            lines.append("📋 Последние транзакции:")
            for t in transactions:
                direction = "📥 Получено от" if t["receiver_id"] == target_id else "📤 Отправлено"
                other_id = t["sender_id"] if t["receiver_id"] == target_id else t["receiver_id"]
                other_user = await db.fetchone("SELECT game_id, first_name FROM users WHERE vk_id = ?", other_id) if other_id else None
                other_name = f"{other_user['first_name']} (ID:{other_user['game_id']})" if other_user else "Система"
                lines.append(f"  • {direction} {other_name}: {t['amount']} {t['currency']} ({t['transaction_type']})")

    return "\n".join(lines)


async def search_player(query: str) -> list:
    if query.isdigit():
        return await db.fetchall(
            "SELECT * FROM users WHERE game_id = ? OR vk_id = ?",
            int(query), int(query)
        )
    return await db.fetchall(
        "SELECT * FROM users WHERE nickname LIKE ? OR first_name LIKE ? OR last_name LIKE ?",
        f"%{query}%", f"%{query}%", f"%{query}%"
    )


async def format_search_results(players: list) -> str:
    if not players:
        return "Никого не найдено."
    lines = ["Результаты поиска:"]
    for p in players:
        nickname = p["nickname"]
        display_name = nickname if nickname else f"{p['first_name']} {p['last_name']}"
        lines.append(f"🆔 {p['game_id']} | {display_name} | LVL {p['level']}")
    return "\n".join(lines)


async def block_player(admin_id: int, target_id: int, block_type: str, duration_days: int = 0) -> tuple:
    if block_type == "freeze" and not await has_permission(admin_id, "players.freeze"):
        return False, "Недостаточно прав для заморозки."
    if block_type == "target" and not await has_permission(admin_id, "players.target_block"):
        return False, "Недостаточно прав для точечной блокировки."
    if block_type == "full" and not await has_permission(admin_id, "players.full_ban"):
        return False, "Недостаточно прав для полного бана."

    if target_id == admin_id:
        return False, "Нельзя заблокировать себя."

    if duration_days > 0:
        until = datetime.now(timezone.utc) + timedelta(days=duration_days)
        await db.execute(
            "UPDATE users SET is_blocked = 1, temporary_blocked_until = ? WHERE vk_id = ?",
            until.isoformat(), target_id
        )
    else:
        await db.execute("UPDATE users SET is_blocked = 1 WHERE vk_id = ?", target_id)

    await db.execute(
        "INSERT INTO admin_log (admin_id, action, details) VALUES (?, 'block', ?)",
        admin_id, f"block_type={block_type}, target={target_id}, duration={duration_days}"
    )
    return True, f"Игрок {target_id} заблокирован ({block_type}, {duration_days or 'навсегда'})."


async def unblock_player(admin_id: int, target_id: int) -> tuple:
    if not await has_permission(admin_id, "players.unblock"):
        return False, "Недостаточно прав для разблокировки."
    await db.execute("UPDATE users SET is_blocked = 0, temporary_blocked_until = NULL WHERE vk_id = ?", target_id)
    await db.execute(
        "INSERT INTO admin_log (admin_id, action, details) VALUES (?, 'unblock', ?)",
        admin_id, f"target={target_id}"
    )
    return True, f"Игрок {target_id} разблокирован."


async def give_item(admin_id: int, target_id: int, item_id: str, quantity: int = 1) -> tuple:
    if not await has_permission(admin_id, "players.give_item"):
        return False, "Недостаточно прав для выдачи предмета."
    item = await db.fetchone("SELECT * FROM items WHERE item_id = ?", item_id)
    if not item:
        return False, "Предмет не найден."

    existing = await db.fetchone(
        "SELECT id, quantity FROM inventory WHERE user_id = ? AND item_id = ?",
        target_id, item_id
    )
    if existing:
        await db.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", quantity, existing["id"])
    else:
        await db.execute(
            "INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)",
            target_id, item_id, quantity
        )

    await db.execute(
        "INSERT INTO admin_log (admin_id, action, details) VALUES (?, 'give_item', ?)",
        admin_id, f"target={target_id}, item={item_id}, qty={quantity}"
    )
    return True, f"Выдано {quantity} шт. {item['name']}."


async def take_item(admin_id: int, target_id: int, item_id: str, quantity: int = 1) -> tuple:
    if not await has_permission(admin_id, "players.take_item"):
        return False, "Недостаточно прав для изъятия предмета."
    inv = await db.fetchone(
        "SELECT id, quantity FROM inventory WHERE user_id = ? AND item_id = ?",
        target_id, item_id
    )
    if not inv or inv["quantity"] < quantity:
        return False, "Недостаточно предметов у игрока."

    await db.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", quantity, inv["id"])
    await db.execute("DELETE FROM inventory WHERE id = ? AND quantity <= 0", inv["id"])
    await db.execute(
        "INSERT INTO admin_log (admin_id, action, details) VALUES (?, 'take_item', ?)",
        admin_id, f"target={target_id}, item={item_id}, qty={quantity}"
    )
    return True, f"Изъято {quantity} шт. предмета {item_id}."


async def give_money(admin_id: int, target_id: int, amount: int) -> tuple:
    if not await has_permission(admin_id, "players.give_money"):
        return False, "Недостаточно прав для выдачи денег."
    await db.execute("UPDATE users SET balance = balance + ? WHERE vk_id = ?", amount, target_id)
    await db.execute(
        "INSERT INTO admin_log (admin_id, action, details) VALUES (?, 'give_money', ?)",
        admin_id, f"target={target_id}, amount={amount}"
    )
    await db.execute(
        "INSERT INTO transactions (sender_id, receiver_id, amount, currency, transaction_type) VALUES (NULL, ?, ?, 'NK', 'admin_give')",
        target_id, amount
    )
    return True, f"Выдано {amount} NK."


async def take_money(admin_id: int, target_id: int, amount: int) -> tuple:
    if not await has_permission(admin_id, "players.take_money"):
        return False, "Недостаточно прав для изъятия денег."
    user = await db.fetchone("SELECT balance FROM users WHERE vk_id = ?", target_id)
    if user["balance"] < amount:
        return False, "У игрока недостаточно денег."

    await db.execute("UPDATE users SET balance = balance - ? WHERE vk_id = ?", amount, target_id)
    await db.execute(
        "INSERT INTO admin_log (admin_id, action, details) VALUES (?, 'take_money', ?)",
        admin_id, f"target={target_id}, amount={amount}"
    )
    await db.execute(
        "INSERT INTO transactions (sender_id, receiver_id, amount, currency, transaction_type) VALUES (?, NULL, ?, 'NK', 'admin_take')",
        target_id, amount
    )
    return True, f"Изъято {amount} NK."